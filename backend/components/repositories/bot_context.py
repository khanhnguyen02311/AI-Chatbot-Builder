from abc import ABC
from sqlalchemy import select, update, delete, and_, or_
from . import BaseRepository
from components.data.models import postgres as PostgresModels
from components.data.schemas import bot_context as BotContextSchemas


class BotContextRepository(BaseRepository, ABC):
    def __init__(self, session):
        super().__init__(session=session)

    def get(self, identifier: int):
        query = select(PostgresModels.BotContext).filter(PostgresModels.BotContext.id == identifier)
        bot_context = self.session.scalar(query)
        return bot_context

    def get_all_by_bot(self, identifier_bot: int):
        query = select(PostgresModels.BotContext).filter(PostgresModels.BotContext.id_bot == identifier_bot)
        bots = self.session.execute(query).scalars().all()
        return bots

    def get_all(self):
        return super().get_all()

    def create(self, new_bot_context: PostgresModels.BotContext):
        self.session.add(new_bot_context)
        self.session.flush()

    def update(self, identifier: int, new_data: BotContextSchemas.BotContextPUT):
        update_query = update(PostgresModels.BotContext).returning(PostgresModels.BotContext).where(PostgresModels.BotContext.id == identifier).values(
            **new_data.model_dump(exclude_none=True))
        new_bot_data = self.session.scalar(update_query)
        self.session.flush()
        return new_bot_data

    def delete(self, identifier: int):
        delete_query = delete(PostgresModels.BotContext).returning(PostgresModels.BotContext).where(PostgresModels.BotContext.id == identifier)
        deleted_bot_context = self.session.scalar(delete_query)
        self.session.flush()
        return deleted_bot_context
