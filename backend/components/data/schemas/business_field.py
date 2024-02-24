from . import BaseModel, BaseORMModel, BaseListModel
from pydantic import Field


class BusinessFieldFULL(BaseORMModel):
    id: int
    field: str


class ListBusinessFieldFULL(BaseListModel):
    root: list[BusinessFieldFULL]
