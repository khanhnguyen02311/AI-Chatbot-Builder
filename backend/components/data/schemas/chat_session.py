from datetime import datetime
from . import BaseModel, BaseORMModel, BaseListModel
from pydantic import Field, model_validator


class ChatSessionFULL(BaseORMModel):
    id: int
    name: str
    human_reply: bool
    time_created: datetime
    id_chat_account: int
    id_bot: int | None
    id_bot_team: int | None


class ChatSessionGET(BaseORMModel):
    id: int
    name: str
    time_created: datetime
    id_bot: int | None
    id_bot_team: int | None


class ListChatSessionGET(BaseListModel):
    root: list[ChatSessionGET]


class ChatSessionPOST(BaseORMModel):
    id_bot: int | None = None
    id_bot_team: int | None = None
    name: str | None = None

    @model_validator(mode="after")
    def at_least_one_bot_type(self):
        if not self.id_bot and not self.id_bot_team:
            raise ValueError("One of id_bot or id_bot_team must be provided")
        if self.id_bot and self.id_bot_team:
            raise ValueError("Only one of id_bot or id_bot_team can be provided")
        return self


class ChatSessionPUT(ChatSessionPOST):
    id: int
