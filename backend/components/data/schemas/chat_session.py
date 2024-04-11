from datetime import datetime
from . import BaseModel, BaseORMModel, BaseListModel
from pydantic import Field


class ChatSessionFULL(BaseORMModel):
    id: int
    id_chat_account: int
    id_bot: int
    name: str
    human_reply: bool
    time_created: datetime


class ListChatSessionFULL(BaseListModel):
    root: list[ChatSessionFULL]


class ChatSessionPOST(BaseORMModel):
    id_chat_account: int
    id_bot: int
    name: str | None = None


class ChatSessionPUT(ChatSessionPOST):
    id: int
