from typing import List, Optional, Any

from cyanprintsdk.api.base_model import CyanBaseModel


class CyanGlobReq(CyanBaseModel):
    root: Optional[str]
    glob: str
    exclude: List[str]
    type: str


class CyanPluginReq(CyanBaseModel):
    name: str
    config: Any


class CyanProcessorReq(CyanBaseModel):
    name: str
    config: Any
    files: List[CyanGlobReq]


class CyanReq(CyanBaseModel):
    processors: List[CyanProcessorReq]
    plugins: List[CyanPluginReq]
