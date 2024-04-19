from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.data.schemas import chat_session as ChatSessionSchemas, chat_message as ChatMessageSchemas
from components.services.account import AccountService
from components.services.chat import ChatService

router = APIRouter(prefix="/sessions")


@router.get("")
def get_chat_sessions(chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    with POSTGRES_SESSION_FACTORY() as session:
        sessions = ChatService(session).get_chat_sessions(chat_account)
        return ChatSessionSchemas.ListChatSessionGET.model_validate(sessions)


@router.post("")
def new_chat_session(session_data: ChatSessionSchemas.ChatSessionPOST, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    with POSTGRES_SESSION_FACTORY() as session:
        new_session = ChatService(session).create_new_chat_session(session_data, chat_account)
        session.commit()
        return new_session


@router.get("/{session_id}/messages")
def get_session_messages(session_id: int, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    with POSTGRES_SESSION_FACTORY() as session:
        messages = ChatService(session).get_session_messages(session_id, chat_account)
        return ChatMessageSchemas.ListChatMessageGET.model_validate(messages)


@router.post("/{session_id}/messages")
def new_chat_message(message_data: ChatMessageSchemas.ChatMessagePOST, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    with POSTGRES_SESSION_FACTORY() as session:
        new_message = ChatService(session).create_new_chat_message(message_data, chat_account)
        session.commit()
        return ChatMessageSchemas.ChatMessageGET.model_validate(new_message)
