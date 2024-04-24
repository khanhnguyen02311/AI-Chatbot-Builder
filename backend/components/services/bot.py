from datetime import datetime
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from components.data import POSTGRES_SESSION_FACTORY, REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import bot as BotSchemas
from components.repositories.bot import BotRepository
from model_agents.agents.account import AccountAgent


class BotService:
    """Handle all bot logic related to accounts"""

    def __init__(self, session):
        self.session = session
        self.bot_repository = BotRepository(session=session)

    def validate_account_bot(self, bot_id: int, account_id: int):
        """Validate if a bot belongs to an account"""

        bot = self.bot_repository.get(bot_id)
        if bot is None or bot.id_account != account_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
        return bot

    def validate_accessible_bot(self, bot_id: int, account_id: int):
        """Validate if a bot is readable by an account"""

        bot = self.bot_repository.get(bot_id)
        if bot is None or not (bot.is_public or bot.id_account == account_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
        return bot

    def get_account_bots(self, account: PostgresModels.Account):
        """Get all bots of an account"""

        return self.bot_repository.get_all_by_account(account.id)

    def get_public_bots(self):
        """Get all public bots"""

        return self.bot_repository.get_all()

    def create_new_bot(self, bot_data: BotSchemas.BotPOST, account: PostgresModels.Account):
        """Create a new bot"""

        new_bot = PostgresModels.Bot(**bot_data.model_dump(), id_account=account.id)
        try:
            _ = AccountAgent(new_bot)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        self.bot_repository.create(new_bot)
        return new_bot

    def update_account_bot(self, bot_id: int, new_data: BotSchemas.BotPUT, account: PostgresModels.Account):
        """Update a bot"""

        self.validate_account_bot(bot_id, account.id)
        try:
            _ = AccountAgent(PostgresModels.Bot(**new_data.model_dump(), id_account=account.id))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        updated_bot = self.bot_repository.update(bot_id, new_data)
        return updated_bot

    def delete_account_bot(self, bot_id: int, account: PostgresModels.Account):
        """Delete a bot"""

        self.validate_account_bot(bot_id, account.id)
        deleted_bot = self.bot_repository.delete(bot_id)
        return deleted_bot
