from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.data.schemas import bot as BotSchemas, bot_context as BotContextSchemas
from components.services.account import AccountService
from components.services.bot import BotService

router = APIRouter()


@router.post("/init-bot-data")
def init_data(account: PostgresModels.Account = Depends(AccountService.validate_token)):
    if account.id_account_role != 1:
        raise HTTPException(402, "Admin account required.")
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session)
        new_bot = BotSchemas.BotPOST(
            name="Quảng Bình Chatbot",
            description="A friendly bot to help tourists in Quang Binh province",
            conf_instruction="Assistant will play the role of a travel chatbot specialized in Vietnamese tourism, mainly including: \n - Answer Human questions about a specific travel location/place.\n - Suggest Human for good tourist/food/accomodation places in the region.\n - Create a detail travel plan from the Human request, including: time range, location, accomodation, food places. For each day, you need to use your tools to search and design a schedule contains time of day (morning/afternoon/night), where to eat, where to play/travel/..., and combine all of these schedules to a final plan to the Human.\nAs a travel chatbot, Assistant needs to answer relevant, accurate and helpful information about Vietnamese tourism based on real data. Assistant will have access to a wide range of tools that can help with the task.\nYou will provide valuable, true information based on real data that you have researched on a wide range of topics related to travel and tourism. Whether the Human need help with a specific question or just want to have a conversation about a particular subject, Assistant is here to assist.\nAs a language model, you are able to generate human-like text based on the input it received, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.\nOverall, Assistant is here to help and provide valuable information to the Human, and will do its best to provide accurate and helpful responses to any questions or requests. If there is anything that Assistant is not sure about or you need more information from the Human, you will let the Human know and ask for clarification or further information.\n",
            conf_model_name="gpt-3.5-turbo-1106",
            conf_model_temperature=0.5,
            is_public=True,
        )
        created_bot = bot_service.create_new_bot(new_bot, account)
        new_bot_context = BotContextSchemas.BotContextPOST(
            filename="testfile.txt",
            description="Things you should know about Quang Binh Province.",
            embedding_model_used="openai@text-embedding-3-small",
            id_bot=created_bot.id,
        )
        new_bot_context = bot_service.create_new_bot_context(new_bot_context, account)
        bot_service.activate_bot_context(new_bot_context)
        session.commit()

        return BotSchemas.BotFULL.model_validate(created_bot).model_dump()
