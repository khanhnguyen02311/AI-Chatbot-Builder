from abc import ABC
from sqlalchemy import select, update, delete, and_, or_
from . import BaseRepository
from components.data.models import postgres as PostgresModels


class ChatMessageRepository(BaseRepository, ABC):
    def __init__(self, session):
        super().__init__(session=session)

    def get(self, identifier: int):
        super().get()

    def get_all(self):
        super().get_all()

    def get_all_by_chat_session(self, chat_session_identifier: int):
        query = select(PostgresModels.ChatMessage).filter(PostgresModels.ChatMessage.id_chat_session == chat_session_identifier)
        chat_messages = self.session.scalars(query).all()
        return chat_messages

    def create(self, new_chat_message: PostgresModels.ChatMessage):
        self.session.add(new_chat_message)
        self.session.flush()

    def update(self, identifier: int, new_data):
        super().update()

    def delete(self, identifier: int):
        pass
