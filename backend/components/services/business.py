import uuid
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from components.data import POSTGRES_SESSION_FACTORY, REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import business as BusinessSchemas
from components.repositories.business import BusinessRepository


class BusinessService:
    """Handle all personal business logic related to account"""

    def __init__(self, session, account: PostgresModels.Account | None = None):
        self.session = session
        self.repository = BusinessRepository(session=session)
        self.account = account

    def get_user_businesses(self):
        businesses = self.repository.get_all_by_account(identifier=self.account.id)
        return businesses

    def get_user_business(self, business_id: int):
        business = self.repository.get(identifier=business_id)
        if business is None or business.id_account != self.account.id:
            return None
        return business

    def create_business(self, business_data: BusinessSchemas.BusinessPOST):
        new_business = PostgresModels.Business(**business_data.model_dump(), id_account=self.account.id)
        self.repository.create(new_business)
        return new_business

    def update_business(self, business_id: int, business_data: BusinessSchemas.BusinessPUT) -> tuple[Any, Any]:
        business = self.get_user_business(business_id)
        if business is None:
            return None, "Business not found"
        updated_business = self.repository.update(identifier=business_id, new_data=business_data)
        return updated_business, None

    def delete_business(self, business_id: int) -> Any:
        business = self.get_user_business(business_id)
        if business is None:
            return "Business not found"
        self.repository.delete(identifier=business_id)
        return None
