from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from components.services.account import AccountService

router = APIRouter()


@router.put("/renew-token")
def renew_token(renewed_tokens: str = Depends(AccountService.renew_token)):
    return JSONResponse(content=renewed_tokens)
