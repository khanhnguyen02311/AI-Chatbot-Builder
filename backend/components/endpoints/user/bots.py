from fastapi import APIRouter, Depends, HTTPException, status
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models.postgres import Account
from components.data.schemas import bot as BotSchemas
from components.services.account import AccountService
from components.services.bot import BotService

router = APIRouter(prefix="/bots")


@router.get("")
def get_all_bots(account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bots = bot_service.get_account_bots(account)
        return BotSchemas.ListBotFULL.model_validate(bots)


@router.post("")
def create_bot(data: BotSchemas.BotPOST, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        new_bot = bot_service.create_new_bot(data, account)
        if new_bot is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bot creation failed")
        session.commit()
        return BotSchemas.BotFULL.model_validate(new_bot)


@router.get("/{bot_id}")
def get_bot(bot_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bot = bot_service.validate_account_bot(bot_id, account.id)
        if bot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
        return BotSchemas.BotFULL.model_validate(bot)


@router.put("/{bot_id}")
def update_bot(bot_id: int, data: BotSchemas.BotPUT, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        updated_bot = bot_service.update_account_bot(bot_id, data, account)
        if updated_bot is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bot update failed")
        session.commit()
        return BotSchemas.BotFULL.model_validate(updated_bot)
