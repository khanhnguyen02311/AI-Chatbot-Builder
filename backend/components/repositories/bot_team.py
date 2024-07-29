from abc import ABC
from sqlalchemy import select, update, delete, and_, or_
from . import BaseRepository
from components.data import REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import bot_team as BotTeamSchemas


class BotTeamRepository(BaseRepository, ABC):
    def __init__(self, session):
        super().__init__(session=session, redis_session=REDIS_SESSION)

    def get(self, identifier: int):
        query = select(PostgresModels.BotTeam).where(PostgresModels.BotTeam.id == identifier)
        bot_team = self.session.scalar(query)
        return bot_team
        # bot_team_data = self.redis_session.get(f"BotTeamFULL:{account_identifier}")
        # if bot_team_data:
        #     return BotTeamSchemas.BotTeamFULL.model_validate_json(bot_team_data)
        # return None

    def get_all_by_account(self, account_identifier: int):
        query = select(PostgresModels.BotTeam).where(PostgresModels.BotTeam.id_account == account_identifier)
        bot_teams = self.session.scalars(query)
        return bot_teams

    def get_all(self):
        super().get_all()

    def create(self, new_bot_team: PostgresModels.BotTeam):
        self.session.add(new_bot_team)
        self.session.flush()

    def update(self, identifier: int, new_data: BotTeamSchemas.BotTeamPUT):
        pass
        update_query = (
            update(PostgresModels.BotTeam)
            .returning(PostgresModels.BotTeam)
            .where(PostgresModels.BotTeam.id == identifier)
            .values(**new_data.model_dump(exclude_none=True))
        )
        new_bot_data = self.session.scalar(update_query)
        self.session.flush()
        return new_bot_data

    def delete(self, identifier: int):
        delete_query = (
            delete(PostgresModels.BotContext)
            .returning(PostgresModels.BotContext)
            .where(PostgresModels.BotContext.id == identifier)
        )
        deleted_bot_context = self.session.scalar(delete_query)
        self.session.flush()
        return deleted_bot_context
