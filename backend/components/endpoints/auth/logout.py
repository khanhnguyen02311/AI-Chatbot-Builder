from fastapi import APIRouter, Depends, Response
from components.services.account import AccountService

router = APIRouter()


@router.post("/logout", dependencies=[Depends(AccountService.deactivate_token)])
def logout():
    return Response(content="Done")
