from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.data.schemas import account as AccountSchemas
from components.services.account import AccountService

router = APIRouter()


@router.post("/init-data")
def init_data(account: PostgresModels.Account = Depends(AccountService.validate_token)):
    if account.id_account_role != 1:
        raise HTTPException(402, "Admin account required.")
