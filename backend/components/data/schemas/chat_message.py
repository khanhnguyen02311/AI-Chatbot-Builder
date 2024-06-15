from datetime import datetime
from . import BaseModel, BaseORMModel, BaseListModel


class ChatMessageFULL(BaseORMModel):
    id: int
    type: str
    content: str
    time_created: datetime
    id_chat_session: int
    id_chat_account: int | None = None


class ChatMessageGET(BaseORMModel):
    id: int
    type: str
    content: str
    time_created: datetime
    # id_chat_session: int
    id_chat_account: int | None = None


class ListChatMessageGET(BaseListModel):
    root: list[ChatMessageGET]


class ChatMessagePOST(BaseORMModel):
    type: str
    content: str
    id_chat_session: int | None = None
