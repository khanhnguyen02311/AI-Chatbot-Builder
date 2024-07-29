from fastapi import APIRouter, Depends, HTTPException, status
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.data.schemas import (
    chat_session as ChatSessionSchemas,
    chat_message as ChatMessageSchemas,
    bot as BotSchemas,
    bot_team as BotTeamSchemas,
)
from components.services.bot import BotService
from components.services.account import AccountService
from components.services.chat import ChatService

from agent_system.agents.account import AccountAgent
from agent_system.agents.graph import AgentGraph

router = APIRouter(prefix="/sessions")


@router.get("")
def get_chat_sessions(chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    with POSTGRES_SESSION_FACTORY() as session:
        sessions = ChatService(session).get_chat_sessions(chat_account)
        return ChatSessionSchemas.ListChatSessionGET.model_validate(sessions)


@router.post("")
def new_chat_session(
    session_data: ChatSessionSchemas.ChatSessionPOST,
    chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat),
):
    with POSTGRES_SESSION_FACTORY() as session:
        new_session = ChatService(session).create_new_chat_session(session_data, chat_account)
        session.commit()
        return ChatSessionSchemas.ChatSessionGET.model_validate(new_session)


@router.get("/{session_id}")
def get_chat_session(
    session_id: int, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)
):
    with POSTGRES_SESSION_FACTORY() as session:
        chat_session = ChatService(session).validate_chat_account_session(session_id, chat_account)
        if chat_session.id_bot is not None:
            bot_key = "bot"
            bot_data = BotService(session).validate_accessible_bot(chat_session.id_bot, chat_account.id_internal_account)
            bot_data_validated = BotSchemas.BotGET.model_validate(bot_data)
        else:
            bot_key = "bot_team"
            bot_data = BotService(session).get_bot_team(chat_session.id_bot_team)  # no validation for now
            bot_data_validated = BotTeamSchemas.BotTeamFULL.model_validate(bot_data)
        data = {
            "chat_session": ChatSessionSchemas.ChatSessionGET.model_validate(chat_session),
            "bot": None,
            "bot_team": None,
        }
        data[bot_key] = bot_data_validated
        return data


@router.get("/{session_id}/messages")
def get_session_messages(
    session_id: int, chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)
):
    with POSTGRES_SESSION_FACTORY() as session:
        messages = ChatService(session).get_session_messages(session_id, chat_account, return_type="model")
        return ChatMessageSchemas.ListChatMessageGET.model_validate(messages)


@router.post("/{session_id}/messages")
def new_chat_message(
    session_id: int,
    message_data: ChatMessageSchemas.ChatMessagePOST,
    chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat),  # validate with JWT token
):
    with POSTGRES_SESSION_FACTORY() as session:
        if message_data.id_chat_session is None or message_data.id_chat_session != session_id:
            message_data.id_chat_session = session_id

        if message_data.type not in PostgresModels.CONSTANTS.ChatMessage_type[3:]:  # check message type
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid message type, must be one of {PostgresModels.CONSTANTS.ChatMessage_type[3:]}",
            )

        chat_service = ChatService(session)
        bot_service = BotService(session)
        chat_session = chat_service.validate_chat_account_session(session_id, chat_account)  # session validation

        # get message history and pass it to bot scratchpad
        session_message_history = chat_service.get_session_messages(
            session_id, chat_account, return_type="langchain", with_validation=False
        )

        if chat_session.id_bot is not None:
            bot = bot_service.validate_accessible_bot(chat_session.id_bot, chat_account.id_internal_account)
            # create response from bot
            account_agent = AccountAgent(bot_data=bot, message_history=session_message_history)
            agent_response = account_agent.generate_response(message_data.content)
        else:
            bot_team, bot_team_members = bot_service.get_bot_team(chat_session.id_bot_team, with_members=True)
            agent_graph = AgentGraph(bot_team=bot_team, agent_bots=bot_team_members, message_history=session_message_history)
            agent_response = agent_graph.generate_response(message_data.content)

        new_message = chat_service.create_new_chat_message(message_data, chat_account, with_validation=False)
        new_response_message = chat_service.create_new_chat_message(
            ChatMessageSchemas.ChatMessagePOST(content=agent_response, type="bot", id_chat_session=session_id),
            chat_account,
            with_validation=False,
        )
        session.commit()

        return {
            "message": ChatMessageSchemas.ChatMessageGET.model_validate(new_message),
            "response": ChatMessageSchemas.ChatMessageGET.model_validate(new_response_message),
        }
