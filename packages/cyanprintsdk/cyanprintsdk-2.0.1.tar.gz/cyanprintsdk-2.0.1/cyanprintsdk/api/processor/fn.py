from typing import Callable, Awaitable

from cyanprintsdk.domain.core.cyan_script import ICyanProcessor
from cyanprintsdk.domain.core.cyan_script_model import CyanProcessorInput
from cyanprintsdk.domain.core.fs.cyan_fs_helper import CyanFileHelper
from cyanprintsdk.domain.processor.output import ProcessorOutput

LambdaProcessorFn = Callable[
    [CyanProcessorInput, CyanFileHelper], Awaitable[ProcessorOutput]
]


class LambdaProcessor(ICyanProcessor):
    def __init__(self, f: LambdaProcessorFn):
        self._f: LambdaProcessorFn = f

    async def process(
        self, i: CyanProcessorInput, file_helper: CyanFileHelper
    ) -> ProcessorOutput:
        return await self._f(i, file_helper)
