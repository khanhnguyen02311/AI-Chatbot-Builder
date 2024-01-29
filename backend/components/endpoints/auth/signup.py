from fastapi import APIRouter, HTTPException, status, Response
from components.data import POSTGRES_SESSION_FACTORY
from components.data.schemas import postgres as PostgresSchema
from components.services.account import AccountService

router = APIRouter()


@router.post("/signup")
def signup(account: PostgresSchema.AccountPOST):
    with POSTGRES_SESSION_FACTORY() as session:
        service = AccountService(session=session)
        new_account, err = service.create_account(data=account)
        if err is not None:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=err)
        session.commit()
        return Response(content="Done")
