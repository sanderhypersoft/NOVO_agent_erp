"""
Dicionário Semântico Canônico do Agente ERP
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import json

@dataclass(frozen=True)
class SemanticConcept:
    tipo: str
    descricao: str
    aliases: List[str] = field(default_factory=list)
    entidades: List[str] = field(default_factory=list)
    regras: List[str] = field(default_factory=list)
    observacoes: List[str] = field(default_factory=list)

class SemanticDictionary:
    def __init__(self, use_supabase: bool = True):
        self.concepts: Dict[str, SemanticConcept] = {}
        self._load_local_concepts()
        
        if use_supabase:
            try:
                from supabase_adapter import SupabaseAdapter
                adapter = SupabaseAdapter()
                response = adapter.get_semantic_dictionary()
                if response.data:
                    for row in response.data:
                        concept_id = row['concept']
                        self.concepts[concept_id] = SemanticConcept(
                            tipo=row.get('type', 'entidade'),
                            descricao=row.get('description', ''),
                            aliases=row.get('synonyms', []),
                            entidades=row.get('required_entities', []),
                            regras=row.get('default_rules', [])
                        )
                    print(f"DEBUG: {len(response.data)} conceitos carregados do Supabase")
            except Exception as e:
                print(f"Warning: Falha ao carregar do Supabase ({e}). Usando local.")

        self._sync_with_local_schema()

    def _load_local_concepts(self):
        self.concepts = {
            "venda_concluida": SemanticConcept(
                tipo="estado_negocio",
                descricao="Venda finalizada e autorizada fiscalmente",
                entidades=["venda"],
                regras=["venda_concluida"],
                observacoes=["Pode existir sem recebimento financeiro"],
            ),
            "faturamento": SemanticConcept(
                tipo="metrica",
                descricao="Soma do valor das vendas válidas",
                entidades=["venda"],
                regras=["venda_concluida"],
            ),
            "ticket_medio": SemanticConcept(
                tipo="metrica",
                descricao="Valor médio por venda válida",
                entidades=["venda"],
                regras=["venda_concluida"],
                observacoes=["Inerentemente parcial por exigir agregação"],
            ),
            "quantidade": SemanticConcept(tipo="metrica", descricao="Contagem de ocorrências"),
            "valor_unitario": SemanticConcept(tipo="metrica", descricao="Preço por unidade"),
            "valor_total": SemanticConcept(tipo="metrica", descricao="Valor bruto de uma operação"),
            "inadimplencia": SemanticConcept(
                tipo="metrica",
                descricao="Valor total de títulos a receber vencidos e não pagos",
                entidades=["receber"],
                regras=["titulo_aberto"],
            ),
            "performance": SemanticConcept(
                tipo="metrica",
                descricao="Indicador geral de desempenho",
                entidades=["venda"],
                regras=["venda_concluida"],
            ),
            "venda": SemanticConcept(tipo="entidade", descricao="Operação de venda"),
            "cliente": SemanticConcept(tipo="entidade", descricao="Cadastro de cliente"),
            "produto": SemanticConcept(tipo="entidade", descricao="Cadastro de produto"),
            "receber": SemanticConcept(tipo="entidade", descricao="Títulos de contas a receber"),
            "pagar": SemanticConcept(tipo="entidade", descricao="Títulos de contas a pagar"),
            "os": SemanticConcept(tipo="entidade", descricao="Ordem de Serviço"),
            "tecnico": SemanticConcept(
                tipo="entidade", 
                descricao="Profissional técnico",
                aliases=["tecnico", "tecnicos", "colaborador"]
            ),
            "fornecedor": SemanticConcept(tipo="entidade", descricao="Cadastro de fornecedores"),
            "materiais_consumidos": SemanticConcept(
                tipo="metrica", 
                descricao="Materiais utilizados em operações",
                aliases=["materiais consumidos", "consumo", "consumidos", "materias consumidos", "materias"],
                entidades=["os", "produto"]
            ),
            "hoje": SemanticConcept(tipo="tempo", descricao="Data atual"),
            "ontem": SemanticConcept(tipo="tempo", descricao="Data anterior"),
            "em_aberto": SemanticConcept(tipo="estado_negocio", descricao="Título ou venda não finaliza"),
            "baixado": SemanticConcept(tipo="estado_negocio", descricao="Título liquidado"),
            "excluido": SemanticConcept(
                tipo="estado_negocio", 
                descricao="Registros marcados como excluídos",
                aliases=["apagado", "deletado"],
                regras=["exclusao_logica"]
            ),
            "ultimas": SemanticConcept(
                tipo="modificador",
                descricao="Ordena descendente por data e limita resultados",
                regras=["ordenar_data_desc", "limite_10"]
            )
        }

    def _sync_with_local_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), "master_schema.json")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
                tables = schema.get("tables", {})
                for table_name in tables:
                    concept_id = table_name.lower()
                    if concept_id not in self.concepts:
                        self.concepts[concept_id] = SemanticConcept(
                            tipo="entidade",
                            descricao=f"Tabela operacional {table_name}",
                            aliases=[concept_id, f"{concept_id}s"]
                        )

    def get(self, concept_name: str) -> Optional[SemanticConcept]:
        return self.concepts.get(concept_name)

    def has_metric(self, name: str) -> bool:
        concept = self.get(name)
        return concept is not None and concept.tipo == "metrica"

    def has_entity(self, name: str) -> bool:
        concept = self.get(name)
        return concept is not None and concept.tipo == "entidade"

    def has_state(self, name: str) -> bool:
        concept = self.get(name)
        return concept is not None and concept.tipo == "estado_negocio"

    def has_time_reference(self, name: str) -> bool:
        concept = self.get(name)
        return concept is not None and concept.tipo == "tempo"

    def has_modifier(self, name: str) -> bool:
        concept = self.get(name)
        return concept is not None and concept.tipo == "modificador"

def get_semantic_dictionary() -> SemanticDictionary:
    return SemanticDictionary()