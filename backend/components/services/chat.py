from datetime import datetime
from fastapi import Depends, HTTPException, status
from langchain_core.messages import HumanMessage, AIMessage
from components.data.models import postgres as PostgresModels
from components.data.schemas import (
    chat_account as ChatAccountSchemas,
    chat_session as ChatSessionSchemas,
    chat_message as ChatMessageSchemas,
)
from components.repositories.chat_account import ChatAccountRepository
from components.repositories.chat_session import ChatSessionRepository
from components.repositories.chat_message import ChatMessageRepository
from components.repositories.bot import BotRepository


class ChatService:
    """Handle all chat logic related to accounts"""

    def __init__(self, session):
        self.session = session

    @staticmethod
    def _convert_message_to_langchain_message(message: PostgresModels.ChatMessage):
        if message.type in PostgresModels.CONSTANTS.ChatMessage_type[:3]:  # bot & admin message counted as AI
            return AIMessage(content=message.content)
        else:
            return HumanMessage(content=message.content)
        # else: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid message type, must be one of {PostgresModels.CONSTANTS.ChatMessage_type}")

    def validate_chat_account_session(self, session_id: int, chat_account: PostgresModels.ChatAccount):
        """Validate if the session belongs to the chat account"""

        chat_session = ChatSessionRepository(self.session).get(session_id)
        if chat_session is None or chat_session.id_chat_account != chat_account.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        return chat_session

    def create_external_chat_account(self, data: ChatAccountSchemas.ChatAccountPOST):
        """Create a new external chat account, mainly used for other platforms"""

        chat_account = PostgresModels.ChatAccount(**data.model_dump(exclude_none=True))
        ChatAccountRepository(self.session).create(chat_account)
        return chat_account

    def create_new_chat_session(
        self, session_data: ChatSessionSchemas.ChatSessionPOST, chat_account: PostgresModels.ChatAccount
    ):
        """Create a new chat session"""

        if session_data.name is None:
            session_data.name = "Session " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if session_data.id_bot is not None:
            # check public / owned bot
            bot = BotRepository(self.session).get(session_data.id_bot)
            if bot is None or not (bot.is_public or bot.id_account == chat_account.id_internal_account):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
        chat_session = PostgresModels.ChatSession(
            **session_data.model_dump(), id_chat_account=chat_account.id, human_reply=False
        )
        self.session.add(chat_session)
        self.session.flush()
        return chat_session

    def get_chat_sessions(self, chat_account: PostgresModels.ChatAccount):
        """Get all chat sessions of a chat account"""

        return ChatSessionRepository(self.session).get_all_by_chat_account(chat_account.id)

    def get_session_messages(
        self,
        session_id: int,
        chat_account: PostgresModels.ChatAccount | None,
        return_type: str = "model",
        with_validation: bool = True,
    ):
        """Get all messages of a chat session"""

        if with_validation:
            self.validate_chat_account_session(session_id, chat_account)
        messages = ChatMessageRepository(self.session).get_all_by_chat_session(session_id)
        if return_type == "model":
            return messages
        elif return_type == "langchain":
            langchain_messages = list(map(self._convert_message_to_langchain_message, messages))
            return langchain_messages
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid return type")

    def create_new_chat_message(
        self,
        message_data: ChatMessageSchemas.ChatMessagePOST,
        chat_account: PostgresModels.ChatAccount,
        with_validation: bool = True,
    ):
        """Create a new chat message"""

        if with_validation:
            self.validate_chat_account_session(message_data.id_chat_session, chat_account)

        if message_data.type in PostgresModels.CONSTANTS.ChatMessage_type[:2]:
            chat_message = PostgresModels.ChatMessage(**message_data.model_dump(exclude_none=True))
        elif message_data.type in PostgresModels.CONSTANTS.ChatMessage_type[2:]:
            chat_message = PostgresModels.ChatMessage(
                **message_data.model_dump(exclude_none=True), id_chat_account=chat_account.id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid message type, must be one of {PostgresModels.CONSTANTS.ChatMessage_type}",
            )

        self.session.add(chat_message)
        self.session.flush()
        return chat_message
