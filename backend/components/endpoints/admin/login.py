from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from components.data import POSTGRES_SESSION_FACTORY
from components.data.schemas import account as AccountSchemas
from components.services.account import AccountService

router = APIRouter()


@router.post("/login")
def login(account: AccountSchemas.AccountLOGIN):
    with POSTGRES_SESSION_FACTORY() as session:
        service = AccountService(session=session)
        admin_tokens, err = service.validate_account(data=account, admin_required=True)
        if err is not None:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=err)
        session.commit()
        return JSONResponse(content=admin_tokens)
