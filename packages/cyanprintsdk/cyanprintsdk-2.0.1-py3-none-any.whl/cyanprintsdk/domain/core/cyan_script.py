from abc import abstractmethod, ABC

from cyanprintsdk.domain.core.cyan import Cyan
from cyanprintsdk.domain.core.cyan_script_model import (
    CyanProcessorInput,
    CyanPluginInput,
)
from cyanprintsdk.domain.core.deterministic import IDeterminism
from cyanprintsdk.domain.core.fs.cyan_fs_helper import CyanFileHelper
from cyanprintsdk.domain.core.inquirer import IInquirer
from cyanprintsdk.domain.plugin.output import PluginOutput
from cyanprintsdk.domain.processor.output import ProcessorOutput


class ICyanTemplate(ABC):
    @abstractmethod
    async def template(self, inquirer: IInquirer, determinism: IDeterminism) -> Cyan:
        pass


class ICyanProcessor(ABC):
    @abstractmethod
    async def process(
        self, i: CyanProcessorInput, file_helper: CyanFileHelper
    ) -> ProcessorOutput:
        pass


class ICyanPlugin(ABC):
    @abstractmethod
    async def plugin(self, i: CyanPluginInput) -> PluginOutput:
        pass
