from typing import List, Union

from cyanprintsdk.api.base_model import CyanBaseModel


class StringArrayAnswerRes(CyanBaseModel):
    answer: List[str]


class StringAnswerRes(CyanBaseModel):
    answer: str


class BoolAnswerRes(CyanBaseModel):
    answer: bool


# Union type for AnswerRes
AnswerRes = Union[StringArrayAnswerRes, StringAnswerRes, BoolAnswerRes]
