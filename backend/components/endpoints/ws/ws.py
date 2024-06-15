from fastapi import APIRouter, Depends, WebSocketException, WebSocketDisconnect, status
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.data.schemas import chat_message as ChatMessageSchemas
from components.services.websocket import CustomWebsocket, WebsocketMessage, WEBSOCKET_SERVICE_SESSION
from components.services.account import AccountService
from components.services.chat import ChatService
from components.services.bot import BotService
from agent_system.agents.account import AccountAgent

router = APIRouter()


@router.get("/one-time-token")
def get_one_time_token(chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    return WEBSOCKET_SERVICE_SESSION.create_one_time_websocket_token(chat_account)


# @router.get("")
# def ws_endpoint_placeholder(token: str):
#     return "Placeholder for Swagger. Using websocket connection in this endpoint instead, pass one-time token in the query"


@router.websocket("")
async def ws_endpoint(ws: CustomWebsocket, token: str):
    chat_account = await WEBSOCKET_SERVICE_SESSION.connect(ws, token)
    try:
        while True:
            ws_message = await ws.receive_json()
            error, new_chat_message = WEBSOCKET_SERVICE_SESSION.validate_user_message(ws_message)
            if error is not None:
                await WEBSOCKET_SERVICE_SESSION.send_message(chat_account.id, WebsocketMessage(type="ERROR", data=f"Invalid message format: {error}"))
                continue

            with POSTGRES_SESSION_FACTORY() as session:
                chat_service = ChatService(session)
                bot_service = BotService(session)
                chat_session = chat_service.validate_chat_account_session(new_chat_message.id_chat_session, chat_account)
                bot = bot_service.validate_accessible_bot(chat_session.id_bot, chat_account.id_internal_account)
                session_message_history = chat_service.get_session_messages(new_chat_message.id_chat_session, chat_account, return_type="langchain", with_validation=False)

                new_message = chat_service.create_new_chat_message(new_chat_message, chat_account, with_validation=False)
                session.flush()
                await WEBSOCKET_SERVICE_SESSION.send_message(chat_account.id,
                                                             WebsocketMessage(type="MESSAGE", data=ChatMessageSchemas.ChatMessageGET.model_validate(new_message)))

                agent_response = AccountAgent(bot_data=bot, message_history=session_message_history).generate_response(new_chat_message.content)
                new_bot_response_message = chat_service.create_new_chat_message(
                    ChatMessageSchemas.ChatMessagePOST(content=agent_response, type="bot", id_chat_session=new_chat_message.id_chat_session),
                    chat_account,
                    with_validation=False)
                await WEBSOCKET_SERVICE_SESSION.send_message(chat_account.id,
                                                             WebsocketMessage(type="MESSAGE", data=ChatMessageSchemas.ChatMessageGET.model_validate(new_bot_response_message)))
                session.commit()

    except WebSocketDisconnect:
        WEBSOCKET_SERVICE_SESSION.disconnect(ws)
