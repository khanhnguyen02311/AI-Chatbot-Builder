from abc import ABC
from sqlalchemy import select, update, delete, and_, or_
from . import BaseRepository
from components.data.models import postgres as PostgresModels
from components.data.schemas import chat_account as ChatAccountSchemas


class ChatAccountRepository(BaseRepository, ABC):
    def __init__(self, session):
        super().__init__(session=session)

    def get(self, identifier: int):
        query = select(PostgresModels.ChatAccount).filter(PostgresModels.ChatAccount.id == identifier)
        chat_account = self.session.scalar(query)
        return chat_account

    def get_by_account_type(self, linked_identifier: int | str, account_type: str):
        if account_type == "internal":
            query = select(PostgresModels.ChatAccount).filter(
                PostgresModels.ChatAccount.id_internal_account == linked_identifier
            )
        else:
            query = select(PostgresModels.ChatAccount).filter(
                and_(
                    PostgresModels.ChatAccount.id_external_account == linked_identifier,
                    PostgresModels.ChatAccount.account_type == account_type,
                )
            )
        chat_account = self.session.scalar(query)
        return chat_account

    def get_all(self):
        super().get_all()

    def create(self, new_chat_account: PostgresModels.ChatAccount):
        self.session.add(new_chat_account)
        self.session.flush()

    def update(self, identifier: int, new_data: ChatAccountSchemas.ChatAccountPUT):
        pass

    def delete(self, identifier: int):
        pass
