from dataclasses import dataclass
from typing import List, Dict, Any

from cyanprintsdk.domain.core.answer import Answer
from cyanprintsdk.domain.core.cyan import Cyan, CyanGlob


@dataclass
class CyanExtensionInput:
    prev_answers: List[Answer]
    prev_cyan: Cyan
    prev_extension_answers: Dict[str, List[Answer]]
    prev_extension_cyans: Dict[str, Cyan]


@dataclass
class CyanProcessorInput:
    read_dir: str
    write_dir: str
    globs: List[CyanGlob]
    config: Any


@dataclass
class CyanPluginInput:
    directory: str
    config: Any
