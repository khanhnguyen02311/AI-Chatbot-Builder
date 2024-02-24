from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models.postgres import Account
from components.data.schemas.account import AccountGET, AccountPUT
from components.services.account import AccountService

router = APIRouter(prefix="/information")


@router.get("")
async def get_user_information(account: Account = Depends(AccountService.validate_token)):
    return AccountGET.model_validate(account)


@router.put("")
async def update_user_information(data: AccountPUT, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        account_service = AccountService(session=session)
        new_account_data, err = account_service.edit_account_information(account.id, data=data)
        if err is not None:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
        session.commit()
        return AccountGET.model_validate(new_account_data)
