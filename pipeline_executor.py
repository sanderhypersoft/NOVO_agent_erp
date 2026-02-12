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

        # 5. SQL BUILDER (Executa se OK ou PARTIAL)
        self.sql_builder.run(context)
        context = self.sql_validator.run(context)
        context = self.confidence_calculator.run(context)

        # 6. LOG DE INTELIGÊNCIA (Supabase)
        self.logger.log(context)

        return context
