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
        self.account_repository = AccountRepository(session=session)
        self.chat_account_repository = ChatAccountRepository(session=session)

    def create_external_chat_account(self, data: ChatAccountSchemas.ChatAccountPOST):
        """Create a new external chat account"""

        account = self.account_repository.get(data.account_id)
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        chat_account = PostgresModels.ChatAccount(**data.model_dump())
        self.chat_account_repository.create(chat_account)
        return chat_account

    def create_new_chat_session(self, session_data: ChatSessionSchemas.ChatSessionPOST):
        """Create a new chat session"""

        chat_account = self.chat_account_repository.get(session_data.chat_account_id)
        if chat_account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        if session_data.name is None:
            session_data.name = "Session " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_session = PostgresModels.ChatSession(**session_data.model_dump(), human_reply=False)
        self.session.add(chat_session)
        self.session.flush()
        return chat_session

    def get_chat_sessions(self, chat_account: PostgresModels.ChatAccount):
        """Get all chat sessions of a chat account"""

        return ChatSessionRepository(self.session).get_all_by_chat_account(chat_account.id)

    def get_session_messages(self, session_id: int):
        """Get all messages of a chat session"""

        return ChatMessageRepository(self.session).get_all_by_chat_session(session_id)
