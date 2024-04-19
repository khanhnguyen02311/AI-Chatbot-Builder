from datetime import datetime
from . import BaseModel, BaseORMModel, BaseListModel
from pydantic import Field


class ChatSessionFULL(BaseORMModel):
    id: int
    name: str
    human_reply: bool
    time_created: datetime
    id_chat_account: int
    id_bot: int


class ChatSessionGET(BaseORMModel):
    id: int
    name: str
    time_created: datetime
    id_bot: int


class ListChatSessionGET(BaseListModel):
    root: list[ChatSessionGET]


class ChatSessionPOST(BaseORMModel):
    id_bot: int
    name: str | None = None


class ChatSessionPUT(ChatSessionPOST):
    id: int
