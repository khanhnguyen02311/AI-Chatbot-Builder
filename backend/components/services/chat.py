from datetime import datetime
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from components.data import POSTGRES_SESSION_FACTORY, REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import chat_account as ChatAccountSchemas, chat_session as ChatSessionSchemas, chat_message as ChatMessageSchemas
from components.repositories.account import AccountRepository
from components.repositories.chat_account import ChatAccountRepository
from components.repositories.chat_session import ChatSessionRepository
from components.repositories.chat_message import ChatMessageRepository


class ChatService:
    """Handle all chat logic related to accounts"""

    def __init__(self, session):
        self.session = session

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

    def create_new_chat_session(self, session_data: ChatSessionSchemas.ChatSessionPOST, chat_account: PostgresModels.ChatAccount):
        """Create a new chat session"""

        if session_data.name is None:
            session_data.name = "Session " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_session = PostgresModels.ChatSession(**session_data.model_dump(), id_chat_account=chat_account.id, human_reply=False)
        self.session.add(chat_session)
        self.session.flush()
        return chat_session

    def get_chat_sessions(self, chat_account: PostgresModels.ChatAccount):
        """Get all chat sessions of a chat account"""

        return ChatSessionRepository(self.session).get_all_by_chat_account(chat_account.id)

    def get_session_messages(self, session_id: int, chat_account: PostgresModels.ChatAccount):
        """Get all messages of a chat session"""

        self.validate_chat_account_session(session_id, chat_account)
        return ChatMessageRepository(self.session).get_all_by_chat_session(session_id)

    def create_new_chat_message(self, message_data: ChatMessageSchemas.ChatMessagePOST, chat_account: PostgresModels.ChatAccount):
        """Create a new chat message"""

        self.validate_chat_account_session(message_data.id_chat_session, chat_account)
        if message_data.type not in PostgresModels.CONSTANTS.ChatMessage_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid message type, must be one of [bot / bot-form / admin / user-text / user-options]")
        chat_message = PostgresModels.ChatMessage(**message_data.model_dump())
        self.session.add(chat_message)
        self.session.flush()
        return chat_message
