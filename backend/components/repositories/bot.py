from abc import ABC
from sqlalchemy import select, update, delete, and_, or_
from . import BaseRepository
from components.data.models import postgres as PostgresModels
from components.data.schemas import bot as BotSchemas


class BotRepository(BaseRepository, ABC):
    def __init__(self, session):
        super().__init__(session=session)

    def get(self, identifier: int):
        query = select(PostgresModels.Bot).filter(PostgresModels.Bot.id == identifier)
        bot = self.session.scalar(query)
        return bot

    def get_all_by_account(self, identifier_account: int):
        query = select(PostgresModels.Bot).filter(PostgresModels.Bot.id_account == identifier_account)
        bots = self.session.execute(query).scalars().all()
        return bots

    def get_all(self):
        query = select(PostgresModels.Bot).filter(PostgresModels.Bot.is_public)
        bots = self.session.execute(query).scalars().all()
        return bots

    def create(self, new_bot: PostgresModels.Bot):
        self.session.add(new_bot)
        self.session.flush()

    def update(self, identifier: int, new_data: BotSchemas.BotPUT):
        update_query = update(PostgresModels.Bot).returning(PostgresModels.Bot).where(PostgresModels.Bot.id == identifier).values(**new_data.model_dump(exclude_none=True))
        new_bot_data = self.session.scalar(update_query)
        self.session.flush()
        return new_bot_data

    def delete(self, identifier: int):
        delete_query = delete(PostgresModels.Bot).returning(PostgresModels.Bot).where(PostgresModels.Bot.id == identifier)
        deleted_bot = self.session.scalar(delete_query)
        self.session.flush()
        return deleted_bot
