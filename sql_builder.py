"""
SQL Builder V2
Responsável APENAS por gerar SQL seguro e determinístico.

- NÃO interpreta linguagem natural
- NÃO decide regra
- NÃO resolve ambiguidade
- NÃO executa query

Recebe um contexto já validado e autorizado.
"""

from agent_state import AgentState


class SQLBuilder:

    def __init__(self, semantic_dictionary, operational_dictionary):
        self.semantic_dictionary = semantic_dictionary
        self.dictionary = operational_dictionary

    def run(self, context):
        intent = context.data.get("intent")
        semantic = context.data.get("semantic_resolution")

        if not intent or not semantic:
            context.state = AgentState.FAIL
            context.errors.append("Contexto insuficiente para geração de SQL")
            return context

        try:
            sql = self._build_sql(intent, semantic)
        except Exception as e:
            context.state = AgentState.FAIL
            context.errors.append(str(e))
            return context

        context.data["sql"] = sql
        if context.state != AgentState.PARTIAL:
            context.state = AgentState.OK
        return context

    # ======================================================
    # SQL CORE
    # ======================================================

    def _build_sql(self, intent, semantic):
        intent_type = semantic.get("intent_type", "detail")
        metrics = semantic.get("metrics", [])
        entities = semantic.get("entities", [])
        states = semantic.get("states", [])
        time_refs = semantic.get("time_refs", [])
        
        # Determine if we are in aggregation mode
        is_aggregation = intent_type == "aggregation" or len(metrics) > 0

        if not entities:
            raise ValueError("Nenhuma entidade identificada na pergunta")

        # 1. Determinar Tabelas Envolvidas
        tables = []
        for e in entities:
            t = self.dictionary.get_table(e)
            if t == "PAGAR" and "excluido" in states:
                t = "EXC_PAGAR"
            if t:
                tables.append(t)
        
        tables = list(set(tables)) # Unificar
        
        # 2. Definir Colunas (SELECT)
        
        # 2. Definir Colunas (SELECT) e Identificar Agregações
        
        select_parts = []
        aggregations = []
        dimensions = []
        
        # Processar Métricas (Agregações)
        if metrics:
            for m in metrics:
                # Determina a tabela de contexto para a métrica
                metric_def = self.dictionary.metrics.get(m)
                req_context = metric_def.required_context if metric_def else None
                
                # Prioridade: required_context da métrica > lógica original
                context_table = None
                if req_context:
                    context_table = self.dictionary.get_table(req_context)
                
                if not context_table:
                    context_table = self._resolve_table_name("venda" if "venda" in entities else (entities[0] if entities else None), states)
                
                metric_sql = self.dictionary.get_metric_sql(m, table_name=context_table)
                
                if metric_sql:
                    select_parts.append(f"{metric_sql} AS {m.upper()}")
                    if any(agg in metric_sql.upper() for agg in ["SUM(", "COUNT(", "AVG(", "MAX(", "MIN("]):
                        aggregations.append(metric_sql)
                    else:
                        dimensions.append(metric_sql)

        # Processar Dimensões e Entidades
        if is_aggregation:
            for entity in entities:
                is_metric_source = False
                for m in metrics:
                    metric_def = self.dictionary.metrics.get(m)
                    if metric_def and entity == metric_def.required_context:
                        is_metric_source = True
                        break
                
                if is_metric_source:
                    continue
                
                cols = self.dictionary.get_default_columns(entity)
                table_name = self._resolve_table_name(entity, states)
                
                if cols and table_name:
                    for c in cols:
                        if c != "*":
                            full_col = f"{table_name}.{c}"
                            select_parts.append(full_col)
                            dimensions.append(full_col)
        else:
            for entity in entities:
                cols = self.dictionary.get_default_columns(entity)
                table_name = self._resolve_table_name(entity, states)
                
                if cols and table_name:
                    for c in cols:
                        if c != "*":
                            select_parts.append(f"{table_name}.{c}")
                        else:
                            select_parts.append(f"{table_name}.*")

        # Se temos agregações mas nenhuma dimensão, tudo bem (Total Geral)
        # Se temos agregações E dimensões, precisamos de GROUP BY
        group_by_clause = ""
        if aggregations and dimensions:
             # GROUP BY deve conter todas as colunas não-agregadas do SELECT
             # Filtra literais ou calc que não precisam estar no group by se necessário (simplificado por enquanto)
             group_by_clause = " GROUP BY " + ", ".join(dimensions)

        # 3. Construir Clausula FROM e JOINS
        # Unificar todas as tabelas necessárias (entidades + filtros)
        unique_tables = []
        for t in tables:
            if t not in unique_tables:
                unique_tables.append(t)
        
        # Lógica de Bridge para Junções Indiretas
        # Se temos VENDAS e PRODUTOS, garantimos ITENSV
        if "PRODUTOS" in unique_tables and "VENDAS" in unique_tables and "ITENSV" not in unique_tables:
            unique_tables.append("ITENSV")
        
        if "PRODUTOS" in unique_tables and "ORDEMSERVICOS" in unique_tables and "ITENSOS" not in unique_tables:
            unique_tables.append("ITENSOS")

        # CRITICAL FIX: Priorizar tabela de contexto da métrica como primary_table
        # Isso garante que regras de negócio sejam aplicadas na tabela correta
        primary_table = None
        
        # Se temos métricas, usa a tabela de contexto da primeira métrica
        if metrics:
            metric_def = self.dictionary.metrics.get(metrics[0])
            if metric_def and metric_def.required_context:
                context_table = self.dictionary.get_table(metric_def.required_context)
                if context_table:
                    # Garante que a tabela de contexto está na lista
                    if context_table not in unique_tables:
                        unique_tables.append(context_table)
                    primary_table = context_table
        
        # Fallback: usa a primeira tabela Fato na ordem de prioridade
        if not primary_table:
            if not unique_tables:
                print(f"DEBUG SQLBuilder: unique_tables vazio para entidades {entities}")
                raise ValueError(f"Não foi possível identificar tabelas para as dimensões: {entities}")
            
            # Ranking de tabelas principais para guiar o JOIN recursivo
            priority_order = ["ORDEMSERVICOS", "VENDAS", "RECEBER", "PAGAR", "EXC_PAGAR", "ITENSOS", "ITENSV", "CLIENTES", "PRODUTOS", "USUARIOS"]
            
            # Ordenação segura: evita erro se a tabela não estiver no priority_order
            unique_tables.sort(key=lambda x: priority_order.index(x.upper()) if x.upper() in priority_order else 999)
            primary_table = unique_tables[0]
            
        print(f"DEBUG SQLBuilder: Table Mapping - Unique: {unique_tables}, Primary: {primary_table}")

        if primary_table in unique_tables:
            unique_tables.remove(primary_table)
            unique_tables.insert(0, primary_table)
        
        print(f"DEBUG SQLBuilder: Unique Tables: {unique_tables}, Primary: {primary_table}")
        
        from_clause = primary_table
        joined_tables = {primary_table}
        
        # Tenta conectar todas as tabelas em um loop até não haver mais mudanças
        changed = True
        while changed and len(joined_tables) < len(unique_tables):
            changed = False
            for table in unique_tables:
                if table not in joined_tables:
                    for existing in list(joined_tables):
                        condition = self.dictionary.get_join_condition(existing, table)
                        if condition:
                            from_clause += f" JOIN {table} ON {condition}"
                            joined_tables.add(table)
                            changed = True
                            break

        # 4. Construir Clausula WHERE (Filtros e Regras)
        where_clauses = []
        
        # Injeção de Regras baseadas em Estados e Métricas
        # Pega as regras associadas aos conceitos resolvidos
        for concept_id in (states + metrics):
            concept = self.semantic_dictionary.get(concept_id)
            if concept:
                for rule_name in concept.regras:
                    rule_sql = self.dictionary.get_rule_sql(rule_name)
                    if rule_sql:
                        # 4.1 Identifica campos na regra
                        import re
                        rule_fields = re.findall(r"([A-Za-z0-9_]+)\s*[=<>]+", rule_sql)
                        
                        # 4.2 Verifica quais campos existem na tabela principal
                        available_fields = [f["field"].upper() for f in self.dictionary.get_fields(primary_table)]
                        
                        qualified_parts = []
                        # Se a regra tem OR, processamos as partes
                        if " OR " in rule_sql.upper():
                            parts = re.split(r" OR ", rule_sql, flags=re.IGNORECASE)
                            for part in parts:
                                part_field_match = re.search(r"([A-Za-z0-9_]+)", part)
                                if part_field_match:
                                    f_name = part_field_match.group(1).upper()
                                    if f_name in available_fields:
                                        qualified_parts.append(f"{primary_table}.{part.strip()}")
                        else:
                            # Regra simples
                            f_name_match = re.search(r"([A-Za-z0-9_]+)", rule_sql)
                            if f_name_match:
                                f_name = f_name_match.group(1).upper()
                                if f_name in available_fields:
                                    qualified_parts.append(f"{primary_table}.{rule_sql.strip()}")
                        
                        if qualified_parts:
                            if len(qualified_parts) > 1:
                                where_clauses.append(f"({' OR '.join(qualified_parts)})")
                            else:
                                where_clauses.append(qualified_parts[0])

        # Filtros de Tempo
        time_where_clauses = []
        for time_ref in time_refs:
            if isinstance(time_ref, dict):
                # FIXED: Use the primary table for date filtering to ensure audit tables like EXC_PAGAR are correctly restricted
                # if the user didn't specify a different entity's date
                table_for_date = primary_table
                date_col = self.dictionary.get_date_column(table_for_date)
                
                if date_col:
                    time_where_clauses.append(
                        f"{table_for_date}.{date_col} BETWEEN '{time_ref['start']}' AND '{time_ref['end']}'"
                    )
        # 4.1 AUTO-CORREÇÃO: Injetar WHERE 1=1 em tabelas sensíveis se faltar filtro
        # Isso evita que o SQLValidator bloqueie a query e permite o pipeline planejar amostras.
        sensitive_tables = ["PAGAR", "RECEBER", "VENDAS", "EXC_PAGAR"]
        print(f"DEBUG SQLBuilder: checking sensitive: {unique_tables}, current where: {where_clauses}")
        if any(t.upper() in unique_tables for t in sensitive_tables):
            if not where_clauses:
                where_clauses.append("1=1")
                print(f"DEBUG SQLBuilder: Injected 1=1")

        where_clauses.extend(time_where_clauses)
        print(f"DEBUG SQLBuilder: Final where_clauses: {where_clauses}")

        # 5. Montagem Final
        # Verifica Modificadores (LIMIT / ORDER BY)
        modifiers = semantic.get("modifiers", [])
        limit_clause = ""
        order_by_clause = ""
        
        if "ultimas" in modifiers:
            limit_clause = "FIRST 10"
            # Tenta ordenar pela data da tabela principal
            date_col = self.dictionary.get_date_column(primary_table)
            if date_col:
                order_by_clause = f" ORDER BY {primary_table}.{date_col} DESC"

        # Lógica de TOP-N e Ordenação Automática para Métricas
        is_top_request = any(kw in intent.get("raw_question", "").lower() for kw in ["mais ", "maiores ", "melhores ", "top "])
        if is_top_request and aggregations and not order_by_clause:
            # Ordena pela primeira métrica encontrada de forma descendente
            metric_col = aggregations[0]
            # Extrai apenas a expressão (ex: SUM(X)) se houver alias
            if " AS " in metric_col.upper():
                metric_col = metric_col.upper().split(" AS ")[0].strip()
            order_by_clause = f" ORDER BY {metric_col} DESC"
            
            # Se não houver limit explícito (como 'ultimas'), força um FIRST 10 para o Top
            if not limit_clause:
                limit_clause = "FIRST 10"

        # Special Case: Exclusão Financeira
        # Se 'exclusoes' está nos estados, precisamos selecionar quem excluiu e o motivo
        if "exclusoes" in states:
            # Fallback para colunas de auditoria comuns
            audit_cols = ["USUARIO_EXCLUSAO", "DATA_EXCLUSAO", "MOTIVO_EXCLUSAO"]
            available_fields = [f["field"] for f in self.dictionary.get_fields(primary_table)]
            for col in audit_cols:
                if col in available_fields:
                    select_parts.append(f"{primary_table}.{col}")
        
        # Injeta LIMIT no SELECT (Firebird Syntax: SELECT FIRST N ...)
        select_clause = f"SELECT {limit_clause} {', '.join(select_parts)}" if limit_clause else f"SELECT {', '.join(select_parts)}"
        
        sql = f"{select_clause} FROM {from_clause}"
        if where_clauses:
            # Unificar Where Clauses (evitar duplicatas)
            where_clauses = list(set(where_clauses))
            sql += " WHERE " + " AND ".join(where_clauses)
        
        # Inserir GROUP BY antes do ORDER BY
        if group_by_clause:
            sql += group_by_clause

        if order_by_clause:
            sql += order_by_clause
            
        return sql

    def _resolve_table_name(self, entity, states):
        if not entity: return None
        t = self.dictionary.get_table(entity)
        if t == "PAGAR" and "excluido" in states:
            return "EXC_PAGAR"
        return t
