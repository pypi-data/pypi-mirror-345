from typing import List, Optional, Dict, cast

from cyanprintsdk.domain.core.answer import (
    Answer,
    BoolAnswer,
    StringAnswer,
    StringArrayAnswer,
    is_string_array_answer,
    is_bool_answer,
    is_string_answer,
)
from cyanprintsdk.domain.core.inquirer import IInquirer
from cyanprintsdk.domain.core.question import (
    Question,
    CheckboxQ,
    ConfirmQ,
    PasswordQ,
    SelectQ,
    TextQ,
    DateQ,
)
from cyanprintsdk.domain.service.out_of_answer_error import OutOfAnswerException


class StatelessInquirer(IInquirer):
    def __init__(self, answers: Dict[str, Answer]):
        self._answers = answers

    def _get_answer(self, q: Question) -> Answer:
        if q.id not in self._answers:
            raise OutOfAnswerException("", q)

        return self._answers[q.id]

    async def checkbox(
        self,
        message: str,
        id: str,
        options: List[str],
        desc: Optional[str] = None,
    ) -> List[str]:
        checkbox_q = CheckboxQ(message=message, options=options, desc=desc, id=id)
        return await self.checkboxQ(checkbox_q)

    async def checkboxQ(self, q: CheckboxQ) -> List[str]:
        answer = self._get_answer(q)
        if is_string_array_answer(answer):
            a = cast(StringArrayAnswer, answer)
            return a.answer

        raise TypeError(
            "Incorrect answer type. Expected: StringArrayAnswer. Got: "
            + str(type(answer))
        )

    async def confirm(self, message: str, id: str, desc: Optional[str] = None) -> bool:
        confirm_q = ConfirmQ(message=message, desc=desc, id=id)
        return await self.confirmQ(confirm_q)

    async def confirmQ(self, q: ConfirmQ) -> bool:
        answer = self._get_answer(q)
        if is_bool_answer(answer):
            b = cast(BoolAnswer, answer)
            return b.answer

        raise TypeError(
            "Incorrect answer type. Expected: BoolAnswer. Got: " + str(type(answer))
        )

    async def password(self, message: str, id: str, desc: Optional[str] = None) -> str:
        password_q = PasswordQ(message=message, desc=desc, id=id)
        return await self.passwordQ(password_q)

    async def passwordQ(self, q: PasswordQ) -> str:
        answer = self._get_answer(q)
        if is_string_answer(answer):
            s = cast(StringAnswer, answer)
            return s.answer

        raise TypeError(
            "Incorrect answer type. Expected: StringAnswer. Got: " + str(type(answer))
        )

    async def select(
        self,
        message: str,
        id: str,
        options: List[str],
        desc: Optional[str] = None,
    ) -> str:
        select_q = SelectQ(message=message, options=options, desc=desc, id=id)
        return await self.selectQ(select_q)

    async def selectQ(self, q: SelectQ) -> str:
        answer = self._get_answer(q)
        if is_string_answer(answer):
            s = cast(StringAnswer, answer)
            return s.answer

        raise TypeError(
            "Incorrect answer type. Expected: StringAnswer. Got: " + str(type(answer))
        )

    async def text(self, message: str, id: str, desc: Optional[str] = None) -> str:
        text_q = TextQ(
            message=message,
            desc=desc,
            validate=None,
            id=id,
        )
        return await self.textQ(text_q)

    async def textQ(self, q: TextQ) -> str:
        answer = self._get_answer(q)
        if is_string_answer(answer):
            s = cast(StringAnswer, answer)
            return s.answer

        raise TypeError(
            "Incorrect answer type. Expected: StringAnswer. Got: " + str(type(answer))
        )

    async def date_select(
        self, message: str, id: str, desc: Optional[str] = None
    ) -> str:
        date_q = DateQ(message=message, desc=desc, id=id)
        return await self.date_selectQ(date_q)

    async def date_selectQ(self, q: DateQ) -> str:
        answer = self._get_answer(q)
        if is_string_answer(answer):
            s = cast(StringAnswer, answer)
            return s.answer

        raise TypeError(
            "Incorrect answer type. Expected: StringAnswer. Got: " + str(type(answer))
        )
