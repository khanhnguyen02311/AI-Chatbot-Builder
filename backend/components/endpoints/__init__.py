from fastapi import APIRouter
from .auth import login, logout, signup, token
from .model import legacy
from .user import information, businesses, scenarios, bots as user_bots
from .public import business_fields, bot_models, bots as public_bots
from .webhook import webhook
from .chat import sessions

tags_metadata = [
    {"name": "Admin", "description": "Operations with application system & user roles"},
    {"name": "Auth", "description": "Operations with authentication methods & user validation"},
    {"name": "User Information", "description": "Operations with user information"},
    {"name": "User Business", "description": "Operations with user businesses"},
    {"name": "User Scenario", "description": "Operations with user scenarios"},
    {"name": "User Bot", "description": "Operations with user bots"},
    {"name": "Model", "description": "Operations with AI models & agents"},
    {"name": "Public", "description": "Publicly available information / utilities"},
    {"name": "Webhook", "description": "Operations with webhook endpoints, used by other platforms / services"},
    {"name": "Chat", "description": "Operations with chat sessions, messages & interactions"},
    {"name": "Others"}
]

super_hub = APIRouter()


@super_hub.get("/", tags=["Others"])
def hello():
    return {"msg": "Hello World"}


super_hub.include_router(login.router, prefix="/auth", tags=["Auth"])
super_hub.include_router(logout.router, prefix="/auth", tags=["Auth"])
super_hub.include_router(signup.router, prefix="/auth", tags=["Auth"])
super_hub.include_router(token.router, prefix="/auth", tags=["Auth"])

super_hub.include_router(legacy.router, prefix="/model", tags=["Model"])

super_hub.include_router(information.router, prefix="/user", tags=["User Information"])
super_hub.include_router(businesses.router, prefix="/user", tags=["User Business"])
super_hub.include_router(scenarios.router, prefix="/user", tags=["User Scenario"])
super_hub.include_router(user_bots.router, prefix="/user", tags=["User Bot"])

super_hub.include_router(business_fields.router, prefix="/public", tags=["Public"])
super_hub.include_router(bot_models.router, prefix="/public", tags=["Public"])
super_hub.include_router(public_bots.router, prefix="/public", tags=["Public"])

super_hub.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])

super_hub.include_router(sessions.router, prefix="/chat", tags=["Chat"])
