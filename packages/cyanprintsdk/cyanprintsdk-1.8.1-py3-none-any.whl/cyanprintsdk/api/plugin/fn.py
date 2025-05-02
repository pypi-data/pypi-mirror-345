from typing import Callable, Awaitable

from cyanprintsdk.domain.core.cyan_script import ICyanPlugin
from cyanprintsdk.domain.core.cyan_script_model import CyanPluginInput
from cyanprintsdk.domain.plugin.output import PluginOutput

LambdaPluginFn = Callable[[CyanPluginInput], Awaitable[PluginOutput]]


class LambdaPlugin(ICyanPlugin):
    def __init__(self, f: LambdaPluginFn):
        self._f: LambdaPluginFn = f

    async def plugin(self, i: CyanPluginInput) -> PluginOutput:
        return await self._f(i)
