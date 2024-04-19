from fastapi import APIRouter, Depends, WebSocketException, WebSocketDisconnect, status
from components.data.models import postgres as PostgresModels
from components.services.websocket import CustomWebsocket, WebsocketService, WEBSOCKET_SERVICE_SESSION
from components.services.account import AccountService

router = APIRouter()


@router.get("/one-time-token")
def get_one_time_token(chat_account: PostgresModels.ChatAccount = Depends(AccountService.validate_token_chat)):
    return WebsocketService.create_one_time_websocket_token(chat_account)


@router.get("")
def ws_endpoint_placeholder(token: str):
    return "Placeholder for Swagger. Using websocket connection in this endpoint instead, pass one-time token in the query"


@router.websocket("")
async def ws_endpoint(ws: CustomWebsocket, token: str):
    chat_account = WebsocketService.validate_one_time_websocket_token(token)
    if chat_account is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid one-time token")
    await WEBSOCKET_SERVICE_SESSION.connect(ws, chat_account)
    try:
        while True:
            new_message = await ws.receive_json()
            await WEBSOCKET_SERVICE_SESSION.process_message(ws, new_message)

    except WebSocketDisconnect:
        WEBSOCKET_SERVICE_SESSION.disconnect(ws)
