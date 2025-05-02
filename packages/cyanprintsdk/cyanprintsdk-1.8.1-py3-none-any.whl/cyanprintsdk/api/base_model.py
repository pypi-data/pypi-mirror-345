from pydantic import BaseModel, ConfigDict  # type: ignore
from pydantic.alias_generators import to_camel  # type: ignore


class CyanBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
