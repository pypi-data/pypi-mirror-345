from dataclasses import dataclass
from typing import Union, List


@dataclass
class StringArrayAnswer:
    answer: List[str]


@dataclass
class StringAnswer:
    answer: str


@dataclass
class BoolAnswer:
    answer: bool


Answer = Union[StringAnswer, StringArrayAnswer, BoolAnswer]


def is_string_answer(a: Answer) -> bool:
    return isinstance(a, StringAnswer)


def is_string_array_answer(a: Answer) -> bool:
    return isinstance(a, StringArrayAnswer)


def is_bool_answer(a: Answer) -> bool:
    return isinstance(a, BoolAnswer)
