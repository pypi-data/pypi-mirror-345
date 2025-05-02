from typing import Union, List

from cyanprintsdk.api.base_model import CyanBaseModel


class StringArrayAnswerReq(CyanBaseModel):
    answer: List[str]


class StringAnswerReq(CyanBaseModel):
    answer: str


class BoolAnswerReq(CyanBaseModel):
    answer: bool


AnswerReq = Union[StringArrayAnswerReq, StringAnswerReq, BoolAnswerReq]


def is_string_answer_req(a: AnswerReq) -> bool:
    return isinstance(a, StringAnswerReq)


def is_string_array_answer_req(a: AnswerReq) -> bool:
    return isinstance(a, StringArrayAnswerReq)


def is_bool_answer_req(a: AnswerReq) -> bool:
    return isinstance(a, BoolAnswerReq)
