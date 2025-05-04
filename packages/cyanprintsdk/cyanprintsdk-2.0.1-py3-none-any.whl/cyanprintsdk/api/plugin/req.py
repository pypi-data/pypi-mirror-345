from typing import Dict, Any

from cyanprintsdk.api.base_model import CyanBaseModel


class PluginReq(CyanBaseModel):
    directory: str
    config: Dict[str, Any]
