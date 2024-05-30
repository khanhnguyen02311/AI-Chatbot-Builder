from datetime import datetime
from . import BaseORMModel, BaseListModel


class BotContextFULL(BaseORMModel):
    id: int
    filename: str
    time_created: datetime
    id_bot: int


class ListBotContextFULL(BaseListModel):
    root: list[BotContextFULL]


class BotContextPOST(BaseORMModel):
    filename: str
    id_bot: int
