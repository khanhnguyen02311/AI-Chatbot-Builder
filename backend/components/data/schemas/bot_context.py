from datetime import datetime
from . import BaseORMModel, BaseListModel


class BotContextFULL(BaseORMModel):
    id: int
    filename: str
    description: str | None
    embedding_model_used: str | None
    time_created: datetime
    id_bot: int


class ListBotContextFULL(BaseListModel):
    root: list[BotContextFULL]


class BotContextPOST(BaseORMModel):
    filename: str
    description: str | None = None
    embedding_model_used: str | None = None
    id_bot: int


class BotContextPUT(BaseORMModel):
    description: str | None = None
    embedding_model_used: str | None = None
