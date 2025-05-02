from typing import Awaitable, Callable

from cyanprintsdk.domain.core.cyan import Cyan
from cyanprintsdk.domain.core.cyan_script import ICyanTemplate
from cyanprintsdk.domain.core.deterministic import IDeterminism
from cyanprintsdk.domain.core.inquirer import IInquirer

LambdaTemplateFn = Callable[[IInquirer, IDeterminism], Awaitable[Cyan]]


class LambdaTemplate(ICyanTemplate):
    def __init__(self, f: LambdaTemplateFn):
        self._f: LambdaTemplateFn = f

    async def template(self, inquirer: IInquirer, determinism: IDeterminism) -> Cyan:
        return await self._f(inquirer, determinism)
