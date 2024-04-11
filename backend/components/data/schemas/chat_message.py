from datetime import datetime
from . import BaseModel, BaseORMModel, BaseListModel
from pydantic import Field


class ChatMessageFULL(BaseORMModel):
    id: int
    id_chat_session: int
    id_chat_account: int | None = None
    message: str
    time_created: datetime


class ChatMessageGET(BaseORMModel):
    id: int
    id_chat_session: int
    id_chat_account: int | None = None
    message: str
    time_created: datetime


class ChatMessagePOST(BaseORMModel):
    id_chat_session: int
    id_chat_account: int
    message: str
