from dataclasses import dataclass
from typing import Dict

from cyanprintsdk.domain.core.answer import Answer


@dataclass
class TemplateInput:
    answers: Dict[str, Answer]
    deterministic_state: Dict[str, str]


@dataclass
class TemplateValidateInput:
    answers: Dict[str, Answer]
    deterministic_state: Dict[str, str]
    validate: str
