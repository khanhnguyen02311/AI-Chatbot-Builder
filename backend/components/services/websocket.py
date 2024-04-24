import uuid
from datetime import datetime, timezone
from typing import Any
from starlette.types import Receive, Scope, Send
from fastapi import WebSocket, WebSocketException, status
from pydantic import BaseModel
from components.data import REDIS_SESSION, POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModel
from components.data.schemas import chat_message as ChatMessageSchemas
from components.repositories.chat_account import ChatAccountRepository
from components.services.chat import ChatService
from model_agents.agents.account import AccountAgent


class CONSTANTS:
    type = ["success", "error", "message", "notification"]


class WebsocketMessage(BaseModel):
    type: str
    data: Any


class CustomWebsocket(WebSocket):
    def __init__(self, scope: Scope, receive: Receive, send: Send):
        super().__init__(scope, receive, send)
        self.time_created = datetime.now(timezone.utc)


# class Connection:
#     def __init__(self, chat_account: PostgresModel.ChatAccount, ws: CustomWebSocket):
#         self.chat_account = chat_account
#         self.ws = ws


class WebsocketService:
    connections_by_chat_account: dict[int, list[CustomWebsocket]]
    connections_by_ws: dict[CustomWebsocket, PostgresModel.ChatAccount]

    def __init__(self):
        self.connections_by_chat_account = {}
        self.connections_by_ws = {}

    @staticmethod
    def create_one_time_websocket_token(chat_account: PostgresModel.ChatAccount):
        token = uuid.uuid4().hex + uuid.uuid4().hex
        REDIS_SESSION.setex(f"WS_token:{token}", 60, str(chat_account.id))
        return {"token": token,
                "type": "one-time"}

    @staticmethod
    def validate_one_time_websocket_token(token: str):
        chat_account_id = REDIS_SESSION.get(f"WS_token:{token}")
        if chat_account_id is None:
            return None
        REDIS_SESSION.delete(f"WS_token:{token}")
        with POSTGRES_SESSION_FACTORY() as session:
            chat_account = ChatAccountRepository(session).get(int(chat_account_id))
            session.expunge_all()
            return chat_account

    async def connect(self, ws: CustomWebsocket, token: str):
        chat_account = self.validate_one_time_websocket_token(token)
        if chat_account is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid one-time token")
        await ws.accept()
        if chat_account.id not in self.connections_by_chat_account:
            self.connections_by_chat_account[chat_account.id] = []
        self.connections_by_chat_account[chat_account.id].append(ws)
        self.connections_by_ws[ws] = chat_account

    def disconnect(self, ws: CustomWebsocket):
        chat_account = self.connections_by_ws.pop(ws)
        self.connections_by_chat_account[chat_account.id].remove(ws)

    async def process_message(self, ws: CustomWebsocket, message: dict):
        chat_account = self.connections_by_ws[ws]
        message_data = ChatMessageSchemas.ChatMessagePOST.model_validate(message)
        try:
            with POSTGRES_SESSION_FACTORY() as session:
                chat_service = ChatService(session)
                chat_service.create_new_chat_message(message_data, chat_account)
                response = WebsocketMessage(type="success", data="Message sent")
                await self.send_message(chat_account.id, response)
                session.commit()
        except Exception as e:
            response = WebsocketMessage(type="error", data=str(e))
            await self.send_message(chat_account.id, response)

    async def send_message(self, chat_account_id: int, message: WebsocketMessage):
        for ws in self.connections_by_chat_account[chat_account_id]:
            await ws.send_json(message.model_dump(mode="json"))


WEBSOCKET_SERVICE_SESSION = WebsocketService()
