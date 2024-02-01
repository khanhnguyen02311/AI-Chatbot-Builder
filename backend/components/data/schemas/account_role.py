from . import BaseModel, BaseORMModel
from pydantic import Field


class AccountRoleFULL(BaseORMModel):
    id: int
    role: str


class AccountRoleGET(BaseORMModel):
    role: str


class AccountRolePUT(BaseORMModel):
    role: str = Field(max_length=64)
