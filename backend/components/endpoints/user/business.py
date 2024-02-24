from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models.postgres import Account
from components.data.schemas import business as BusinessSchemas
from components.services.account import AccountService
from components.services.business import BusinessService

router = APIRouter(prefix="/business")


@router.get("")
async def get_business_list(account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        service = BusinessService(session=session, account=account)
        businesses = service.get_personal_businesses()
        return BusinessSchemas.ListBusinessGET.model_validate(businesses)


@router.post("")
async def create_business(data: BusinessSchemas.BusinessPOST, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        service = BusinessService(session=session, account=account)
        new_business = service.create_business(data)
        session.commit()
        return BusinessSchemas.BusinessGET.model_validate(new_business)


@router.get("/{business_id}")
async def get_business(business_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        service = BusinessService(session=session, account=account)
        business, err = service.get_business_data(business_id)
        if err is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
        return BusinessSchemas.BusinessGET.model_validate(business)


@router.put("/{business_id}")
async def update_business(business_id: int, data: BusinessSchemas.BusinessPUT, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        service = BusinessService(session=session, account=account)
        updated_business, err = service.update_business(identifier=business_id, business_data=data)
        if err is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
        session.commit()
        return BusinessSchemas.BusinessGET.model_validate(updated_business)


@router.delete("/{business_id}")
def delete_business(business_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        service = BusinessService(session=session, account=account)
        business, err = service.get_business_data(business_id)
        if err is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
        service.delete_business(business_id)
        session.commit()
        return BusinessSchemas.BusinessGET.model_validate(business)
