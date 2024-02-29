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

    def _validate_personal_business(self, business_id: int) -> tuple[Any, Any]:
        business = self.repository.get(identifier=business_id)
        if business is None or business.id_account != self.account.id:
            return False, None
        return True, business

    def get_personal_businesses(self):
        businesses = self.repository.get_all_by_account(identifier=self.account.id)
        return businesses

    def get_business_data(self, business_id: int) -> tuple[Any, Any]:
        valid, business = self._validate_personal_business(business_id)
        if not valid:
            return None, "Business not found"
        return business, None

    def create_business(self, business_data: BusinessSchemas.BusinessPOST):
        new_business = PostgresModels.Business(**business_data.model_dump(), id_account=self.account.id)
        self.repository.create(new_business)
        return new_business

    def update_business(self, identifier: int, business_data: BusinessSchemas.BusinessPUT) -> tuple[Any, Any]:
        business, err = self.get_business_data(identifier)
        if err is not None:
            return None, err
        updated_business = self.repository.update(identifier=identifier, new_data=business_data)
        return updated_business, None

    def delete_business(self, business_id: int) -> tuple[Any, Any]:
        business, err = self.get_business_data(business_id)
        if err is not None:
            return None, err
        business = self.repository.delete(identifier=business_id)
        return business, None
