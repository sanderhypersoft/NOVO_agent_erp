import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class MetricDefinition:
    sql_template: str
    target_role: Optional[str] = None
    required_context: Optional[str] = None
    filters: List[str] = field(default_factory=list)

class OperationalDictionary:
    def __init__(self, use_supabase: bool = True):
        self.schema_path = os.path.join(os.path.dirname(__file__), "master_schema.json")
        self.data = self._load_schema()
        self.metrics = {} # Será carregado do Supabase ou Fallback
        self.entity_map = {}
        self.rules_sql = {
            "venda_concluida": "STATUS = 'F'",
            "titulo_aberto": "STATUS = 'A'",
            "exclusao_financeira": "TIPO = 'E'",
            "exclusao_logica": "STATUS = 'X' OR STATUS_OS = 'X'",
            "filtro_tecnico": "CARGO = 'TECNICO'",
            "os_item_nao_cancelado": "CANCELADO <> 'S'"
        }

        if use_supabase:
            self._load_from_supabase()
        else:
            self._load_fallbacks()

        # Sincronização Dinâmica: Adiciona tabelas do schema se não no mapa
        for table in self.data.get("tables", {}):
            lower_table = table.lower()
            if lower_table not in self.entity_map:
                self.entity_map[lower_table] = table.upper()

    def _load_schema(self) -> dict:
        if not os.path.exists(self.schema_path):
            return {"tables": {}}
        with open(self.schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_from_supabase(self):
        try:
            from supabase_adapter import SupabaseAdapter
            adapter = SupabaseAdapter()
            response = adapter.get_operational_dictionary()
            if response.data:
                for row in response.data:
                    concept = row['concept']
                    table = row['table_name']
                    field = row['field_name']
                    is_metric = row.get('is_metric', False)
                    custom_sql = row.get('custom_sql')

                    # Mapear Entidade
                    if table and not is_metric:
                        self.entity_map[concept] = table
                    
                    # Mapear Métrica
                    if is_metric:
                        template = custom_sql or "SUM({table}.{field})"
                        self.metrics[concept] = MetricDefinition(
                            sql_template=template,
                            target_role="MATERIAL_VALUE" if "SUM" in template else None,
                            required_context=concept.split('_')[0] # Heurística simples
                        )
                print(f"DEBUG: {len(response.data)} mapeamentos operacionais do Supabase")
        except Exception as e:
            print(f"Warning: Falha Supabase Operational ({e}). Usando fallbacks.")
            self._load_fallbacks()

    def _load_fallbacks(self):
        self.entity_map = {
            "venda": "VENDAS", 
            "cliente": "CLIENTES", 
            "pagar": "PAGAR",
            "os": "ORDEMSERVICOS",
            "tecnico": "USUARIOS",
            "tecnicos": "USUARIOS",
            "itens": "ITENSOS",
            "usuario": "USUARIOS",
            "exclusao_pagar": "EXC_PAGAR",
            "exclusao_usuario": "EXC_USUARIO"
        }
        self.metrics["materiais_consumidos"] = MetricDefinition(
            sql_template="SUM({table}.QTD)",
            target_role=None,
            required_context="itensos"
        )
        self.metrics["quantidade"] = MetricDefinition(
            sql_template="COUNT({table}.CONTROLE)",
            target_role=None
        )
        self.metrics["valor_total"] = MetricDefinition(
            sql_template="SUM({table}.{field})",
            target_role="VALUE"
        )

    def get_table(self, entity: str) -> Optional[str]:
        if entity.upper() in self.data.get("tables", {}):
            return entity.upper()
        return self.entity_map.get(entity.lower())

    def get_fields(self, table_name: str) -> List[dict]:
        return self.data.get("tables", {}).get(table_name.upper(), [])

    def get_field_by_role(self, table_name: str, role: str) -> Optional[str]:
        fields = self.get_fields(table_name)
        for f in fields:
            if f.get("role") == role:
                return f.get("field")
        return None

    def get_metric_sql(self, metric: str, table_name: str = None) -> Optional[str]:
        definition = self.metrics.get(metric)
        if not definition: return None
        if not definition.target_role: return definition.sql_template
        
        target_table = table_name or (self.get_table(definition.required_context) if definition.required_context else None)
        if not target_table: return None

        field_name = self.get_field_by_role(target_table, definition.target_role)
        if field_name:
            return definition.sql_template.format(table=target_table, field=field_name)
        
        # Fallback para métricas fixas (sem field_role)
        if "{table}" in definition.sql_template and not field_name:
             return definition.sql_template.format(table=target_table)
             
        return definition.sql_template

    def get_date_column(self, table_name: str) -> Optional[str]:
        col = self.get_field_by_role(table_name, "TEMPORAL")
        if col: return col
        fallbacks = {"VENDAS": "DATA", "RECEBER": "EMISSAO", "PAGAR": "EMISSAO", "EXC_PAGAR": "EMISSAO"}
        return fallbacks.get(table_name.upper())

    def get_join_condition(self, table_a: str, table_b: str) -> Optional[str]:
        bridges = {
            ("VENDAS", "ITENSV"): "VENDAS.CTRVENDA = ITENSV.CTRVENDA",
            ("ITENSV", "PRODUTOS"): "ITENSV.PRODUTO = PRODUTOS.CODIGO", 
            ("VENDAS", "CLIENTES"): "VENDAS.CLIENTE = CLIENTES.CODIGO",
            ("ORDEMSERVICOS", "ITENSOS"): "ORDEMSERVICOS.CTROS = ITENSOS.CTROS",
            ("ITENSOS", "PRODUTOS"): "ITENSOS.PRODUTO = PRODUTOS.CODIGO",
            ("ORDEMSERVICOS", "USUARIOS"): "ORDEMSERVICOS.VENDEDOR = USUARIOS.CONTROLE",
            ("PAGAR", "USUARIOS"): "PAGAR.USUARIO = USUARIOS.CONTROLE",
            ("EXC_PAGAR", "EXC_USUARIO"): "EXC_PAGAR.CONTROLE = EXC_USUARIO.CTRMOVI AND EXC_USUARIO.MOVI = 'PG'",
            ("EXC_PAGAR", "USUARIOS"): "EXC_PAGAR.USUARIO = USUARIOS.CONTROLE"
        }
        return bridges.get((table_a.upper(), table_b.upper())) or bridges.get((table_b.upper(), table_a.upper()))

    def get_rule_sql(self, rule_name: str) -> Optional[str]:
        return self.rules_sql.get(rule_name)

    def get_default_columns(self, table_name: str) -> List[str]:
        actual_table = self.get_table(table_name) or table_name
        fields = self.get_fields(actual_table)
        if fields:
            return [f["field"] for f in fields[:5]]
        return ["*"]
