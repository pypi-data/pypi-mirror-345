from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Union, Callable


@dataclass
class CheckboxQ:
    message: str
    options: List[str]
    id: str  # Unique identifier for the question
    desc: Optional[str] = None
    validate: None = None
    # validate: Optional[Callable[[str], Optional[str]]] = None


@dataclass
class ConfirmQ:
    message: str
    id: str  # Unique identifier for the question
    desc: Optional[str] = None
    default: Optional[bool] = None
    error_message: Optional[str] = None
    validate: None = None
    # validate: Optional[Callable[[str], Optional[str]]] = None


@dataclass
class DateQ:
    message: str
    id: str  # Unique identifier for the question
    desc: Optional[str] = None
    validate: Optional[Callable[[str], Optional[str]]] = None
    default: Optional[date] = None
    min_date: Optional[date] = None
    max_date: Optional[date] = None


@dataclass
class PasswordQ:
    message: str
    id: str  # Unique identifier for the question
    desc: Optional[str] = None
    validate: Optional[Callable[[str], Optional[str]]] = None
    confirmation: Optional[bool] = None


@dataclass
class SelectQ:
    message: str
    options: List[str]
    id: str  # Unique identifier for the question
    desc: Optional[str] = None
    validate: None = None
    # validate: Optional[Callable[[str], Optional[str]]] = None


@dataclass
class TextQ:
    message: str
    id: str  # Unique identifier for the question
    desc: Optional[str] = None
    validate: Optional[Callable[[str], Optional[str]]] = None
    default: Optional[str] = None
    initial: Optional[str] = None


# Type hint for a generic question
Question = Union[TextQ, SelectQ, PasswordQ, DateQ, ConfirmQ, CheckboxQ]
