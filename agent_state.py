from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any

class AgentState(Enum):
    OK = "OK"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"
    AMBIGUOUS = "AMBIGUOUS"

@dataclass
class AgentContext:
    question: str
    state: AgentState = AgentState.OK
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: int = 0

    def __post_init__(self):
        if "original_question" not in self.data:
            self.data["original_question"] = self.question
