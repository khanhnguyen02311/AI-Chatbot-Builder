from typing import Optional, Any
from datetime import datetime
from pydantic import Json
from . import BaseORMModel, BaseListModel
from .account import AccountGET
from .business import BusinessGET
from pydantic import Field


class ScenarioFULL(BaseORMModel):
    id: int
    name: str
    time_created: datetime
    flow: dict[str, Any]
    id_account: int
    rel_account: AccountGET | None = None
    id_business: int
    rel_business: BusinessGET | None = None


class ScenarioGET(BaseORMModel):
    id: int
    name: str
    time_created: datetime
    flow: dict[str, Any]
    id_business: int


class ScenarioPOST(BaseORMModel):
    name: str = Field(min_length=5, max_length=64)
    flow: Json[Any]
    id_business: int


class ScenarioPUT(ScenarioPOST):
    pass
