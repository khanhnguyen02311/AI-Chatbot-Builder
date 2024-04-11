from fastapi import APIRouter
from components.data import POSTGRES_SESSION_FACTORY
from components.data.schemas import bot as BotSchemas
from components.services.bot import BotService

router = APIRouter()


@router.get("/bots")
def get_all_public_bots():
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bots = bot_service.get_public_bots()
        return BotSchemas.ListBotGET.model_validate(bots)
