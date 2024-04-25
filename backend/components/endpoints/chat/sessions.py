from fastapi import APIRouter, Depends, HTTPException, status
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.data.schemas import chat_session as ChatSessionSchemas, chat_message as ChatMessageSchemas, bot as BotSchemas
from components.services.bot import BotService
from components.services.account import AccountService
from components.services.chat import ChatService
from model_agents.agents.account import AccountAgent

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
        return ChatSessionSchemas.ChatSessionGET.model_validate(new_session)


@router.get("/{session_id}")
def get_chat_session(session_id: int, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    with POSTGRES_SESSION_FACTORY() as session:
        chat_session = ChatService(session).validate_chat_account_session(session_id, chat_account)
        bot = BotService(session).validate_accessible_bot(chat_session.id_bot, chat_account.id_internal_account)
        return {"chat_session": ChatSessionSchemas.ChatSessionGET.model_validate(chat_session),
                "bot": BotSchemas.BotGET.model_validate(bot)}


@router.get("/{session_id}/messages")
def get_session_messages(session_id: int, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    with POSTGRES_SESSION_FACTORY() as session:
        messages = ChatService(session).get_session_messages(session_id, chat_account, return_type="model")
        return ChatMessageSchemas.ListChatMessageGET.model_validate(messages)


@router.post("/{session_id}/messages")
def new_chat_message(session_id: int, message_data: ChatMessageSchemas.ChatMessagePOST, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    with POSTGRES_SESSION_FACTORY() as session:
        if message_data.id_chat_session is None or message_data.id_chat_session != session_id:
            message_data.id_chat_session = session_id
        if message_data.type not in PostgresModels.CONSTANTS.ChatMessage_type[3:]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid message type, must be one of {PostgresModels.CONSTANTS.ChatMessage_type[3:]}")

        chat_service = ChatService(session)
        bot_service = BotService(session)
        chat_session = chat_service.validate_chat_account_session(session_id, chat_account)
        bot = bot_service.validate_accessible_bot(chat_session.id_bot, chat_account.id_internal_account)
        session_messages = chat_service.get_session_messages(session_id, chat_account, return_type="langchain", with_validation=False)
        new_message = chat_service.create_new_chat_message(message_data, chat_account, with_validation=False)

        response = AccountAgent(bot_data=bot, message_history=session_messages).generate_response(message_data.content)
        new_bot_message = chat_service.create_new_chat_message(
            ChatMessageSchemas.ChatMessagePOST(content=response, type="bot", id_chat_session=session_id),
            chat_account,
            with_validation=False)
        session.commit()

        return {"message": ChatMessageSchemas.ChatMessageGET.model_validate(new_message),
                "response": ChatMessageSchemas.ChatMessageGET.model_validate(new_bot_message)}
