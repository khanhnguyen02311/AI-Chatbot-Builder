from typing import Optional
from datetime import datetime
from . import BaseORMModel, BaseListModel
from .account import AccountGET
from pydantic import Field
from faker import Faker


class BusinessFULL(BaseORMModel):
    id: int
    name: str
    description: str
    fields: list[str]
    time_created: datetime
    address: str | None = None
    phone: str | None = None
    website_url: str | None = None
    id_account: int
    rel_account: AccountGET | None = None
    # rel_business_products: List[BusinessProductGET] | None = None
    # rel_scenarios: List[ScenarioGET] | None = None


class BusinessGET(BaseORMModel):
    id: int
    name: str
    description: str
    fields: list[str]
    address: str | None = None
    phone: str | None = None
    website_url: str | None = None
    time_created: datetime


class ListBusinessGET(BaseListModel):
    root: list[BusinessGET]


class BusinessPOST(BaseORMModel):
    name: str = Field(min_length=5, max_length=64)
    description: str = Field(min_length=5)
    fields: list[str] = Field(min_items=1, max_items=5)
    address: str | None = Field(max_length=256, default=None)
    phone: str | None = Field(max_length=16, default=None)
    website_url: str | None = Field(max_length=64, default=None)


class BusinessPUT(BusinessPOST):
    pass
