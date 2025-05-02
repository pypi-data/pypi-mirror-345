from typing import Optional, Dict, Union

from cyanprintsdk.api.base_model import CyanBaseModel
from cyanprintsdk.api.core.cyan_res import CyanRes
from cyanprintsdk.api.core.question_res import QuestionRes


class TemplateValidRes(CyanBaseModel):
    valid: Optional[str]


class TemplateFinalRes(CyanBaseModel):
    cyan: CyanRes
    type: str = "final"


class TemplateQnARes(CyanBaseModel):
    deterministic_state: Dict[str, str]
    question: QuestionRes
    type: str = "questionnaire"


# Union type for TemplateRes
TemplateRes = Union[TemplateQnARes, TemplateFinalRes]
