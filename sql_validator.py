from agent_state import AgentState


class SQLValidationError(Exception):
    pass


class SQLValidator:
    """
    Final SQL safety and senior-quality validator.
    This layer does NOT fix SQL — it only approves or blocks.
    """
    def __init__(self, semantic_dictionary):
        self.semantic_dictionary = semantic_dictionary

    FORBIDDEN_PATTERNS = [
        "select *",
        "delete ",
        "update ",
        "drop ",
        "truncate ",
        "insert ",
        ";--",
    ]

    def run(self, context):
        sql = context.data.get("sql")

        if not sql:
            context.state = AgentState.FAIL
            context.errors.append("SQL não gerado")
            return context

        sql_lower = sql.lower().strip()

        try:
            self._validate_forbidden_patterns(sql_lower)
            self._validate_select_columns(sql_lower)
            self._validate_where_clause(sql_lower)
            self._validate_group_by(sql_lower)
            self._validate_dates(sql_lower)
        except SQLValidationError as e:
            context.state = AgentState.FAIL
            context.errors.append(str(e))
            return context

        if context.state != AgentState.PARTIAL:
            context.state = AgentState.OK
        return context

    # -------------------- RULES --------------------

    def _validate_forbidden_patterns(self, sql: str):
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in sql:
                raise SQLValidationError(f"Padrão SQL proibido detectado: {pattern}")

    def _validate_select_columns(self, sql: str):
        # if sql.startswith("select *"):
        #    raise SQLValidationError("Uso de SELECT * é proibido")
        pass

    def _validate_where_clause(self, sql: str):
        sensitive_keywords = ["vendas", "caixa", "receber", "pagar", "exc_pagar"]
        if any(k in sql for k in sensitive_keywords):
            if " where " not in sql:
                raise SQLValidationError("Consultas sensíveis exigem cláusula WHERE")
            
            # Se for apenas 1=1, é um sinal de que o pipeline deve agir no modo proteção
            if "where 1=1" in sql and " and " not in sql:
                # Não lança erro, mas sinaliza (isso será tratado no PipelineExecutor)
                pass

    def _validate_group_by(self, sql: str):
        aggregates = ["sum(", "count(", "avg("]
        select_part = sql.split("from")[0]
        if any(a in select_part for a in aggregates):
            if "," in select_part and "group by" not in sql:
                raise SQLValidationError("Uso de múltiplos campos com agregação exige GROUP BY explícito")

    def _validate_dates(self, sql: str):
        if "current_date" in sql or "now()" in sql:
            raise SQLValidationError("Datas devem ser explícitas ou parametrizadas")
