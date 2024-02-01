from fastapi import APIRouter
from .auth import login, logout, signup, token
from .model import legacy

super_hub = APIRouter()

super_hub.include_router(login.router, prefix="/auth", tags=["auth"])
super_hub.include_router(logout.router, prefix="/auth", tags=["auth"])
super_hub.include_router(signup.router, prefix="/auth", tags=["auth"])
super_hub.include_router(token.router, prefix="/auth", tags=["auth"])

super_hub.include_router(legacy.router, prefix="/model", tags=["model"])
