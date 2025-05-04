from dataclasses import dataclass
from typing import Any


@dataclass
class PluginInput:
    directory: str
    config: Any
