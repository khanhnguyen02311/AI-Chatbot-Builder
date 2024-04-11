from fastapi import APIRouter, HTTPException, status, Response
from components.data import POSTGRES_SESSION_FACTORY
from components.data.schemas import account as AccountSchema
from components.services.account import AccountService

router = APIRouter()


@router.post("/signup")
def signup(account: AccountSchema.AccountPOST):
    with POSTGRES_SESSION_FACTORY() as session:
        service = AccountService(session=session)
        new_account, err = service.create_account_pair(data=account)
        if err is not None:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=err)
        session.commit()
        return Response(content="Done")
