from . import BaseModel, BaseORMModel
from pydantic import Field


class BotModelFULL(BaseORMModel):
    id: int
    name: str


class BotModelGET(BaseORMModel):
    name: str


class BotModelPUT(BaseORMModel):
    id: int
    name: str = Field(max_length=64)
