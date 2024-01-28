from . import BaseModel, BaseORMModel
from pydantic import constr, Field


class AccountLOGIN(BaseModel):
    username_or_email: str = Field(max_length=128)
    password: str = Field(min_length=8, max_length=128)


class AccountFULL(BaseORMModel):
    id: int
    name: str
    username: str
    email: str
    time_created: str


class AccountGET(BaseORMModel):
    id: int
    name: str
    username: str
    email: str


class AccountPOST(BaseORMModel):
    username: str = Field(min_length=8, max_length=128, pattern=r"^[a-zA-Z0-9_!@#$%^&*+-/]+$")
    password: str = Field(min_length=8, max_length=128, pattern=r"^[a-zA-Z0-9_!@#$%^&*+-/]+$")
    email: str = Field(max_length=128, pattern=r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,4})+$")


class AccountPUT(BaseORMModel):
    name: str | None = Field(max_length=128, default=None)
    username: str | None = Field(min_length=8, max_length=128, pattern=r"^[a-zA-Z0-9_!@#$%^&*+-/]+$", default=None)
    email: str | None = Field(max_length=128, pattern=r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,4})+$", default=None)
