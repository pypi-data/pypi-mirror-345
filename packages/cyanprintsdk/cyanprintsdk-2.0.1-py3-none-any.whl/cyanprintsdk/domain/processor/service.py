from cyanprintsdk.domain.core.cyan_script import ICyanProcessor
from cyanprintsdk.domain.core.cyan_script_model import CyanProcessorInput
from cyanprintsdk.domain.core.fs.cyan_fs_helper import CyanFileHelper
from cyanprintsdk.domain.processor.input import ProcessorInput
from cyanprintsdk.domain.processor.output import ProcessorOutput


class ProcessorService:
    def __init__(self, processor: ICyanProcessor):
        self._processor = (
            processor  # Leading underscore indicates a "private" attribute
        )

    async def process(self, i: ProcessorInput) -> ProcessorOutput:
        read_directory = i.read_directory
        write_directory = i.write_directory
        globs = i.globs
        config = i.config

        helper = CyanFileHelper(read_directory, write_directory, globs)
        return await self._processor.process(
            CyanProcessorInput(
                read_dir=read_directory,
                write_dir=write_directory,
                globs=globs,
                config=config,
            ),
            helper,
        )
