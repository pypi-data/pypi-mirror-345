from cyanprintsdk.domain.core.cyan_script import ICyanPlugin
from cyanprintsdk.domain.core.cyan_script_model import CyanPluginInput
from cyanprintsdk.domain.plugin.input import PluginInput
from cyanprintsdk.domain.plugin.output import PluginOutput


class PluginService:
    def __init__(self, plugin: ICyanPlugin):
        self._plugin = plugin  # Leading underscore indicates a "private" attribute

    async def plug(self, i: PluginInput) -> PluginOutput:
        directory = i.directory
        config = i.config
        return await self._plugin.plugin(
            CyanPluginInput(directory=directory, config=config)
        )
