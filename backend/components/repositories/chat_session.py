from abc import ABC

from sqlalchemy import select, update, delete
from . import BaseRepository
from components.data import REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import chat_session as ChatSessionSchemas


class ChatSessionRepository(BaseRepository, ABC):
    def __init__(self, session):
        super().__init__(session=session)

    def get(self, identifier: int):
        query = select(PostgresModels.ChatSession).filter(PostgresModels.ChatSession.id == identifier)  # .join(PostgresModels.Account)
        chat_session = self.session.scalar(query)
        return chat_session

    def get_all(self):
        super().get_all()

    def get_all_by_chat_account(self, chat_account_identifier: int):
        query = select(PostgresModels.ChatSession).filter(PostgresModels.ChatSession.id_chat_account == chat_account_identifier).order_by(
            PostgresModels.ChatSession.id.desc())
        chat_sessions = self.session.scalars(query).all()
        return chat_sessions

    def create(self, new_chat_session: PostgresModels.ChatSession):
        self.session.add(new_chat_session)
        self.session.flush()

    def update(self, identifier: int, new_data: ChatSessionSchemas.ChatSessionPUT):
        super().update()
        # query = update(PostgresModels.Business).returning(PostgresModels.Business).where(PostgresModels.Business.id == identifier).values(**new_data.model_dump(exclude_none=True))
        # new_business_data = self.session.scalar(query)
        # self.session.flush()
        # return new_business_data

    def delete(self, identifier: int):
        delete_query = delete(PostgresModels.ChatSession).where(PostgresModels.ChatSession.id == identifier)
        self.session.execute(delete_query)
        self.session.flush()
        return object
