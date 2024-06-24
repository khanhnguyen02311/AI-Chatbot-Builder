from datetime import datetime
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from configurations.envs import ChatModels
from components.data import POSTGRES_SESSION_FACTORY, REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import bot as BotSchemas
from components.data.schemas import bot_context as BotContextSchemas
from components.repositories.bot import BotRepository
from components.repositories.bot_context import BotContextRepository
from agent_system.data.loader import DataLoader
from agent_system.data.retriever import DataRetriever
from agent_system.agents.account import AccountAgent


class BotService:
    """Handle all bot logic related to accounts"""

    def __init__(self, session):
        self.session = session
        self.bot_repository = BotRepository(session=session)
        self.bot_context_repository = BotContextRepository(session=session)

    def validate_account_bot(self, bot_id: int, account_id: int):
        """Validate if a bot belongs to an account"""

        bot = self.bot_repository.get(bot_id)
        if bot is None or bot.id_account != account_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
        return bot

    def validate_accessible_bot(self, bot_id: int, account_id: int):
        """Validate if a bot is readable by an account (public bot OR account's bot)"""

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
            _ = AccountAgent(PostgresModels.Bot(**new_data.model_dump(exclude_none=True), id_account=account.id))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        updated_bot = self.bot_repository.update(bot_id, new_data)
        return updated_bot

    def delete_account_bot(self, bot_id: int, account: PostgresModels.Account):
        """Delete a bot"""

        self.validate_account_bot(bot_id, account.id)
        self.get_bot_contexts(bot_id, account)
        deleted_bot = self.bot_repository.delete(bot_id)
        return deleted_bot

    def get_bot_context(self, bot_id: int, bot_context_id: int, account: PostgresModels.Account):
        """Get a bot context"""

        self.validate_account_bot(bot_id, account.id)
        bot_context = self.bot_context_repository.get(bot_context_id)
        if bot_context.id_bot != bot_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot context not found")
        return bot_context

    def get_bot_contexts(self, bot_id: int, account: PostgresModels.Account):
        """Get all contexts of a bot"""

        self.validate_account_bot(bot_id, account.id)
        return self.bot_context_repository.get_all_by_bot(bot_id)

    def create_new_bot_context(self, new_context_data: BotContextSchemas.BotContextPOST, account: PostgresModels.Account):
        """Create a new context"""

        self.validate_account_bot(new_context_data.id_bot, account.id)
        if new_context_data.embedding_model_used is not None and new_context_data.embedding_model_used not in list(
            ChatModels.ALLOWED_EMBEDDING_MODELS.keys()
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Embedding model not supported for now")

        new_context = PostgresModels.BotContext(**new_context_data.model_dump(exclude_none=True))
        self.bot_context_repository.create(new_context)
        return new_context

    def update_bot_context(
        self,
        bot_id: int,
        bot_context_id: int,
        context_data: BotContextSchemas.BotContextPUT,
        account: PostgresModels.Account,
    ):
        """Update existed bot context"""
        _ = self.get_bot_context(bot_id, bot_context_id, account)  # just for validation
        if context_data.embedding_model_used is not None and context_data.embedding_model_used not in list(
            ChatModels.ALLOWED_EMBEDDING_MODELS.keys()
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Embedding model not supported for now")

        updated_bot_context = self.bot_context_repository.update(bot_context_id, context_data)
        return updated_bot_context

    def delete_bot_context(self, bot_context_id: int, account: PostgresModels.Account):
        """Delete a context"""

        bot_context = self.bot_context_repository.get(bot_context_id)
        self.validate_account_bot(bot_context.id_bot, account.id)
        deleted_context = self.bot_context_repository.delete(bot_context_id)
        return deleted_context

    def activate_bot_context(self, bot_context: PostgresModels.BotContext):
        existed_bot_context_chunks = DataRetriever().get_existed_bot_context_vectors(bot_context.id_bot, bot_context.id)
        print(existed_bot_context_chunks)
        if len(existed_bot_context_chunks[0]) > 0:
            print(f"Bot context {bot_context.id} already activated. Exit.")
            return
        data_loader = DataLoader()
        parsed_text = data_loader.parse_to_text(bot_context.filename)
        if not parsed_text:
            print(f"Parsing error for BotContext {bot_context.id}. Exit.")
            # todo: send failed notification
            return
        parsed_chunks = data_loader.split_text(parsed_text, 700, 0)
        result = data_loader.load_chunks_to_qdrant(parsed_chunks, bot_context)
        print(f"Parsing for BotContext {bot_context.id} is done. Result: {str(result)}")
        # send result notification
