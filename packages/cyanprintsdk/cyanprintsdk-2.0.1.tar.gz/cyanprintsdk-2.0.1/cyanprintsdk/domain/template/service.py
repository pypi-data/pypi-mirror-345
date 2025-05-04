from typing import Optional

from cyanprintsdk.domain.core.cyan_script import ICyanTemplate
from cyanprintsdk.domain.core.question import Question
from cyanprintsdk.domain.service.out_of_answer_error import OutOfAnswerException
from cyanprintsdk.domain.service.stateless_determinism import StatelessDeterminism
from cyanprintsdk.domain.service.stateless_inquirer import StatelessInquirer
from cyanprintsdk.domain.template.input import TemplateInput, TemplateValidateInput
from cyanprintsdk.domain.template.output import (
    TemplateQnAOutput,
    TemplateOutput,
    TemplateFinalOutput,
)


class TemplateService:
    def __init__(self, template: ICyanTemplate):
        self._template = template

    async def template(self, answer: TemplateInput) -> TemplateOutput:
        i = StatelessInquirer(answer.answers)
        d = StatelessDeterminism(answer.deterministic_state)

        try:
            r = await self._template.template(i, d)
            return TemplateFinalOutput(data=r)
        except OutOfAnswerException as e:
            q: Question = e.question
            return TemplateQnAOutput(deterministic_state=d.states, question=q)
        except Exception as e:
            raise e

    async def validate(self, answer: TemplateValidateInput) -> Optional[str]:
        i = StatelessInquirer(answer.answers)
        d = StatelessDeterminism(answer.deterministic_state)

        try:
            await self._template.template(i, d)
            raise RuntimeError("Not supposed to reach here for validation!")
        except OutOfAnswerException as e:
            q: Question = e.question
            validate_result = q.validate(answer.validate) if q.validate else None
            return validate_result
        except Exception as e:
            raise e
