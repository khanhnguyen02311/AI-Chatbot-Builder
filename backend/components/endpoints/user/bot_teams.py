from fastapi import APIRouter, Depends, HTTPException, status
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models.postgres import Account
from components.data.schemas import bot_team as BotTeamSchemas
from components.services.account import AccountService
from components.services.bot import BotService

router = APIRouter(prefix="/bot-teams")


@router.get("")
def get_all_bot_teams(account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bot_teams = bot_service.get_account_bot_teams(account)
        return BotTeamSchemas.ListBotTeamFULL.model_validate(bot_teams)


@router.post("")
def create_bot_team(data: BotTeamSchemas.BotTeamPOST, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        new_bot_team = bot_service.create_bot_team(data, account)
        if new_bot_team is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bot Team creation failed")
        session.commit()
        return BotTeamSchemas.BotTeamFULL.model_validate(new_bot_team)


@router.get("/{bot_team_id}")
def get_bot_team(bot_team_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bot_team = bot_service.validate_account_bot_team(bot_team_id, account.id)
        if bot_team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot Team not found")
        return BotTeamSchemas.BotTeamFULL.model_validate(bot_team)


@router.put("/{bot_team_id}")
def update_bot_team(
    data: BotTeamSchemas.BotTeamPUT, bot_team_id: int, account: Account = Depends(AccountService.validate_token)
):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        updated_bot_team = bot_service.update_bot_team(bot_team_id, data, account)
        if updated_bot_team is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot Team creation failed.")
        session.commit()
        return BotTeamSchemas.BotTeamFULL.model_validate(updated_bot_team)


@router.delete("/{bot_team_id}")
def delete_bot_team(bot_team_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bot_service.delete_bot_team(bot_team_id, account)
        session.commit()
        return {"message": "Bot Team deleted"}


@router.get("/{bot_team_id}/set-default")
def set_default_bot_team(bot_team_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        _ = bot_service.validate_account_bot_team(bot_team_id, account.id)
        bot_service.set_default_facebook_bot_team(bot_team_id)
        return {"message": "Bot Team set as default"}
