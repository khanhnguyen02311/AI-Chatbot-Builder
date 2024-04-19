from datetime import datetime
from . import BaseModel, BaseORMModel, BaseListModel
from pydantic import Field


class BotFULL(BaseORMModel):
    id: int
    name: str
    is_public: bool
    description: str
    conf_model_temperature: float
    conf_model_name: str
    conf_instruction: str
    conf_external_data: str | None
    time_created: datetime
    id_account: int


class ListBotFULL(BaseListModel):
    root: list[BotFULL]


class BotGET(BaseORMModel):
    id: int
    name: str
    description: str
    id_account: int


class ListBotGET(BaseListModel):
    root: list[BotGET]


class BotPOST(BaseORMModel):
    name: str = Field(max_length=64)
    description: str = Field(min_length=16)
    is_public: bool
    conf_model_temperature: float = Field(ge=0.0, le=1.0)
    conf_model_name: str = Field(max_length=64)
    conf_instruction: str


class BotPUT(BotPOST):
    pass
