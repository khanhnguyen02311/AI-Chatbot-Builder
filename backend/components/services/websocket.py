import uuid
from datetime import datetime, timezone
from typing import Any
from starlette.types import Receive, Scope, Send
from fastapi import WebSocket, WebSocketException, status
from pydantic import BaseModel, field_validator
from components.data import REDIS_SESSION, POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.data.schemas import chat_message as ChatMessageSchemas
from components.repositories.chat_account import ChatAccountRepository
from components.services.chat import ChatService
from agent_system.agents.account import AccountAgent


class WebsocketMessage(BaseModel):
    type: str
    data: Any

    @field_validator("type")
    def validate_message_type(cls, value):
        if value not in ["MESSAGE", "NOTIFICATION", "SUCCESS", "ERROR"]:
            raise ValueError('Invalid message type, must be one of ["message", "notification", "success", "error"]')


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
    connections_by_ws: dict[CustomWebsocket, PostgresModels.ChatAccount]

    def __init__(self):
        self.connections_by_chat_account = {}
        self.connections_by_ws = {}

    @staticmethod
    def create_one_time_websocket_token(chat_account: PostgresModels.ChatAccount):
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

    @staticmethod
    def validate_user_message(message: dict) -> tuple[str | None, ChatMessageSchemas.ChatMessagePOST | None]:
        try:
            message_data = ChatMessageSchemas.ChatMessagePOST.model_validate(message)
            if message_data.type not in PostgresModels.CONSTANTS.ChatMessage_type[3:]:
                return f"Invalid message type, must be one of {PostgresModels.CONSTANTS.ChatMessage_type[3:]}", None
            if message_data.id_chat_session is None:
                return "id_chat_session is required", None
            return None, message_data

        except Exception as e:
            return str(e), None

    async def connect(self, ws: CustomWebsocket, token: str):
        chat_account = self.validate_one_time_websocket_token(token)
        if chat_account is None:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid one-time token")
        await ws.accept()
        if chat_account.id not in self.connections_by_chat_account:
            self.connections_by_chat_account[chat_account.id] = []
        self.connections_by_chat_account[chat_account.id].append(ws)
        self.connections_by_ws[ws] = chat_account
        return chat_account

    def disconnect(self, ws: CustomWebsocket):
        chat_account = self.connections_by_ws.pop(ws)
        self.connections_by_chat_account[chat_account.id].remove(ws)

    async def send_message(self, chat_account_id: int, message: WebsocketMessage):
        for ws in self.connections_by_chat_account[chat_account_id]:
            await ws.send_json(message.model_dump(mode="json"))


WEBSOCKET_SERVICE_SESSION = WebsocketService()
