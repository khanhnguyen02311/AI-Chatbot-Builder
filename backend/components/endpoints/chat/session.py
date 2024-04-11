from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.services.account import AccountService
from components.services.chat import ChatService

router = APIRouter(prefix="/sessions")


@router.get("/")
def get_chat_sessions(chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    with POSTGRES_SESSION_FACTORY() as session:
        pass


@router.get("/{session_id}/messages")
def get_session_messages(session_id: int, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    pass


@router.post("/{session_id}/messages")
def new_chat_message(session_id: int, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    pass
