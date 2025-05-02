from typing import Dict

from cyanprintsdk.api.base_model import CyanBaseModel

from cyanprintsdk.api.core.answer_req import AnswerReq


class TemplateValidateReq(CyanBaseModel):
    answers: Dict[str, AnswerReq]
    deterministic_states: Dict[str, str]
    validate: str


class TemplateAnswerReq(CyanBaseModel):
    answers: Dict[str, AnswerReq]
    deterministic_states: Dict[str, str]
