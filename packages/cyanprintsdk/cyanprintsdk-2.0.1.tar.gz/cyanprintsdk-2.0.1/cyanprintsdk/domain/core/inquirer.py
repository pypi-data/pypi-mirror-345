from abc import ABC, abstractmethod
from typing import List, Optional

from cyanprintsdk.domain.core.question import (
    CheckboxQ,
    ConfirmQ,
    PasswordQ,
    SelectQ,
    TextQ,
    DateQ,
)


class IInquirer(ABC):

    @abstractmethod
    async def checkbox(
        self,
        message: str,
        id: str,
        options: List[str],
        desc: Optional[str] = None,
    ) -> List[str]:
        pass

    @abstractmethod
    async def checkboxQ(self, q: CheckboxQ) -> List[str]:
        pass

    @abstractmethod
    async def confirm(self, message: str, id: str, desc: Optional[str] = None) -> bool:
        pass

    @abstractmethod
    async def confirmQ(self, q: ConfirmQ) -> bool:
        pass

    @abstractmethod
    async def password(self, message: str, id: str, desc: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def passwordQ(self, q: PasswordQ) -> str:
        pass

    @abstractmethod
    async def select(
        self,
        message: str,
        id: str,
        options: List[str],
        desc: Optional[str] = None,
    ) -> str:
        pass

    @abstractmethod
    async def selectQ(self, q: SelectQ) -> str:
        pass

    @abstractmethod
    async def text(self, message: str, id: str, desc: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def textQ(self, q: TextQ) -> str:
        pass

    @abstractmethod
    async def date_select(
        self, message: str, id: str, desc: Optional[str] = None
    ) -> str:
        pass

    @abstractmethod
    async def date_selectQ(self, q: DateQ) -> str:
        pass
