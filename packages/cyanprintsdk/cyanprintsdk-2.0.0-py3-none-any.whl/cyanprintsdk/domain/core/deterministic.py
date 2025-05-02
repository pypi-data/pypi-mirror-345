from abc import ABC, abstractmethod
from typing import Callable


class IDeterminism(ABC):
    @abstractmethod
    def get(self, key: str, origin: Callable[[], str]) -> str:
        pass
