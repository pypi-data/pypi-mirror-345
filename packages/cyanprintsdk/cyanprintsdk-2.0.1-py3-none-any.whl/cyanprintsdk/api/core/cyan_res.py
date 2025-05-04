from typing import List, Optional, Any

from cyanprintsdk.api.base_model import CyanBaseModel


class CyanGlobRes(CyanBaseModel):
    root: Optional[str]
    glob: str
    exclude: List[str]
    type: str


class CyanPluginRes(CyanBaseModel):
    name: str
    config: Any  # 'Any' is used for the 'unknown' type


class CyanProcessorRes(CyanBaseModel):
    name: str
    config: Any  # 'Any' is used for the 'unknown' type
    files: List[CyanGlobRes]


class CyanRes(CyanBaseModel):
    processors: List[CyanProcessorRes]
    plugins: List[CyanPluginRes]


# No need for explicit export statements in Python
