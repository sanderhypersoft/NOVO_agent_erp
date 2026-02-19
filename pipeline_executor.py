"""
Pipeline Executor – V2

Contrato técnico do pipeline do agente ERP.
Este arquivo contém APENAS código Python válido.
"""

from agent_state import AgentState, AgentContext
from normalizer import Normalizer
from intent_extractor import IntentExtractor
from semantic_mapper import SemanticMapper
from rule_engine import RuleEngine
from ambiguity_analyzer import AmbiguityAnalyzer
from sql_builder import SQLBuilder
from sql_validator import SQLValidator
from confidence_calculator import ConfidenceCalculator


class PipelineExecutor:
    def __init__(self, semantic_dictionary=None, operational_dictionary=None):
        from semantic_dictionary import get_semantic_dictionary
        from operational_dictionary import OperationalDictionary
        from intelligence_logger import IntelligenceLogger

        self.semantic_dictionary = semantic_dictionary or get_semantic_dictionary()
        self.operational_dictionary = operational_dictionary or OperationalDictionary()
        self.logger = IntelligenceLogger()

        self.normalizer = Normalizer()
        self.intent_extractor = IntentExtractor(self.semantic_dictionary)
        self.semantic_mapper = SemanticMapper(self.semantic_dictionary)
        self.rule_engine = RuleEngine(self.semantic_dictionary)
        self.ambiguity_analyzer = AmbiguityAnalyzer(self.semantic_dictionary)

        self.sql_builder = SQLBuilder(
            semantic_dictionary=self.semantic_dictionary,
            operational_dictionary=self.operational_dictionary,
        )

        self.sql_validator = SQLValidator(self.semantic_dictionary)
        self.confidence_calculator = ConfidenceCalculator(self.semantic_dictionary)

    def run(self, question: str) -> AgentContext:
        context = AgentContext(question)

        context = self.normalizer.run(context)
        context = self.intent_extractor.run(context)
        context = self.semantic_mapper.run(context)
        # 3. RULE ENGINE
        self.rule_engine.run(context)
        
        # 4. AMBIGUITY ANALYZER
        self.ambiguity_analyzer.run(context)
        
        # Bloqueia se houver falha crítica antes do SQL
        if context.state in [AgentState.FAIL, AgentState.AMBIGUOUS]:
            self.logger.log(context)
            return context

        # 5. MODO MULTI-STEP REASONING (Novo)
        # Se a pergunta é complexa, podemos gerar múltiplos SQLs
        # Por enquanto, focamos em um ciclo que tenta resolver sub-partes se necessário
        
        # 5.1 Geração do Primeiro SQL (ou Principal)
        context = self.sql_builder.run(context)
        context = self.sql_validator.run(context)
        
        if context.state == AgentState.FAIL:
             self.logger.log(context)
             return context

        # 6. EXECUÇÃO DO SQL ATUAL
        self._execute_sql_step(context)

        # 7. SYNTHESIS (Novo): Consolida resultados de múltiplos SQLs ou agregações
        self._synthesize_results(context)
        
        # FINAL: Logar Inteligência
        context = self.confidence_calculator.run(context)
        self.logger.log(context)

        return context

    def _execute_sql_step(self, context: AgentContext):
        sql = context.data.get("sql")
        if sql and context.state in [AgentState.OK, AgentState.PARTIAL]:
            # 1. Detecção de Consulta Sensível sem Filtro (Auto-Corrigida)
            sql_clean = sql.lower().replace("\n", " ")
            is_full_scan = "where 1=1" in sql_clean and " and " not in sql_clean
            
            try:
                from firebird_executor import FirebirdExecutor
                executor = FirebirdExecutor()

                # 2. Se for Full Scan, rodar COUNT(*) primeiro para contexto
                if is_full_scan:
                    import re
                    table_match = re.search(r"FROM\s+([A-Za-z0-9_]+)", sql, re.IGNORECASE)
                    if table_match:
                        table_name = table_match.group(1)
                        count_sql = f"SELECT COUNT(*) AS TOTAL FROM {table_name}"
                        count_res = executor.execute(count_sql)
                        if count_res:
                            total = count_res[0].get("TOTAL")
                            if "rule_warnings" not in context.data:
                                context.data["rule_warnings"] = []
                            context.data["rule_warnings"].append(
                                f"Consulta geral em {table_name} (Total: {total}). Aplicada amostra FIRST 100."
                            )
                    
                    # Força FIRST 100 se já não houver limite
                    if "FIRST " not in sql.upper():
                        sql = sql.replace("SELECT ", "SELECT FIRST 100 ", 1)

                results = executor.execute(sql)
                
                if "steps_results" not in context.data:
                    context.data["steps_results"] = []
                
                context.data["steps_results"].append({
                    "sql": sql,
                    "results": results,
                    "is_full_scan": is_full_scan
                })

                if not context.data.get("results"):
                    context.data["results"] = results
                    if results:
                        context.data["columns"] = list(results[0].keys())
                    else:
                        context.data["columns"] = []
                
            except ImportError:
                context.data["results_note"] = "Driver fdb não instalado. Execução real-time disponível apenas no modo LOCAL."
            except Exception as e:
                context.data["execution_error"] = str(e)

    def _synthesize_results(self, context: AgentContext):
        """
        Consolida os resultados técnicos em uma estrutura amigável para resposta.
        Ex: Se temos uma lista de usuários com contagens, extrai o Total e o Top 1.
        """
        results = context.data.get("results")
        if not results:
            return

        summary = {}
        
        # 1. Identifica métricas nos resultados
        semantic = context.data.get("semantic_resolution", {})
        entities = semantic.get("entities", [])
        
        if len(results) >= 1:
            # Temos um conjunto de dados
            total_count = 0
            total_value = 0.0
            top_entity_val = -1
            top_entity_name = None

            for row in results:
                # Soma quantidade
                if "QUANTIDADE" in row:
                    val = int(row["QUANTIDADE"] or 0)
                    total_count += val
                    if val > top_entity_val:
                        top_entity_val = val
                        # Busca o nome da entidade (ex: USUARIO, NOME, CLIENTE)
                        for k, v in row.items():
                            if k not in ["QUANTIDADE", "VALOR_TOTAL"] and v:
                                top_entity_name = str(v)
                                break
                
                # Soma valor
                if "VALOR_TOTAL" in row:
                    total_value += float(row["VALOR_TOTAL"] or 0)

            # Se for apenas uma linha e tiver métricas, o total é o valor da linha
            if len(results) == 1:
                row = results[0]
                summary["total_quantidade"] = int(row.get("QUANTIDADE") or 0) if "QUANTIDADE" in row else None
                summary["valor_consolidado"] = float(row.get("VALOR_TOTAL") or 0) if "VALOR_TOTAL" in row else None
            else:
                # Resultados agregados de múltiplas linhas
                if total_count > 0:
                    summary["total_quantidade"] = total_count
                if total_value > 0:
                    summary["valor_consolidado"] = total_value
                if top_entity_name:
                    summary["destaque"] = {
                        "valor": top_entity_val,
                        "nome": top_entity_name,
                        "contexto": "usuario_com_mais_acoes" if "usuario" in entities else "top_resultado"
                    }

        context.data["summary"] = summary
