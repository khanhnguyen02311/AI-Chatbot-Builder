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
    graph_main_bot: bool
    graph_connected_bots: list[int]
    time_created: datetime
    id_account: int


class ListBotFULL(BaseListModel):
    root: list[BotFULL]


class BotGET(BaseORMModel):
    id: int
    name: str
    description: str
    id_account: int
    graph_main_bot: bool
    graph_connected_bots: list[int]


class ListBotGET(BaseListModel):
    root: list[BotGET]


class BotPOST(BaseORMModel):
    name: str = Field(max_length=64)
    description: str = Field(min_length=16)
    is_public: bool
    conf_model_temperature: float = Field(ge=0.0, le=1.0)
    conf_model_name: str = Field(max_length=64)
    conf_instruction: str
    graph_main_bot: bool = True
    graph_connected_bots: list[int] = []


class BotPUT(BotPOST):
    # name: str | None = Field(max_length=64, default=None)
    # description: str | None = Field(min_length=16, default=None)
    # is_public: bool | None = None
    # conf_model_temperature: float | None = Field(ge=0.0, le=1.0, default=None)
    # conf_model_name: str | None = Field(max_length=64, default=None)
    # conf_instruction: str | None = None
    pass
