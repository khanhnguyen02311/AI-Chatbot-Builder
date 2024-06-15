from datetime import datetime
from . import BaseModel, BaseORMModel
from pydantic import Field, model_validator


class ChatAccountFULL(BaseORMModel):
    id: int
    account_type: str
    name: str | None = None
    id_internal_account: int | None = None
    id_external_account: str | None = None
    time_created: datetime


class ChatAccountGET(BaseORMModel):
    account_type: str
    name: str | None = None
    id_internal_account: int | None = None
    id_external_account: str | None = None


class ChatAccountPOST(BaseORMModel):
    account_type: str = Field(max_length=16, default="internal")
    name: str = Field(min_length=5, max_length=64)
    id_internal_account: int | None = None
    id_external_account: str | None = None

    @model_validator(mode="after")
    def at_least_one_account(self):
        if not self.id_internal_account and not self.id_external_account:
            raise ValueError("At least one of id_internal_account or id_external_account must be provided")

    def model_dump_internal(self):
        return self.model_dump(exclude={"id_external_account", "name"})

    def model_dump_external(self):
        return self.model_dump(exclude={"id_internal_account"})


class ChatAccountPUT(ChatAccountPOST):
    id: int
