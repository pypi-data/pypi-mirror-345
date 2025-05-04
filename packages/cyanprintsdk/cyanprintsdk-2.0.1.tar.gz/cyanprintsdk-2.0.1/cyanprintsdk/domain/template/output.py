from dataclasses import dataclass
from typing import Dict, Union

from cyanprintsdk.domain.core.cyan import Cyan
from cyanprintsdk.domain.core.question import Question


@dataclass
class TemplateQnAOutput:
    deterministic_state: Dict[str, str]
    question: Question


@dataclass
class TemplateFinalOutput:
    data: Cyan


# Union type to represent either TemplateQnAOutput or TemplateFinalOutput
TemplateOutput = Union[TemplateQnAOutput, TemplateFinalOutput]


def is_final(output: TemplateOutput) -> bool:
    return isinstance(output, TemplateFinalOutput) and output.data is not None


def is_qna(output: TemplateOutput) -> bool:
    return isinstance(output, TemplateQnAOutput) and output.question is not None
