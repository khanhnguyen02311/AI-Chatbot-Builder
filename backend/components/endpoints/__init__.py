from fastapi import APIRouter
from .auth import login, logout, signup, token
from .model import legacy
from .user import information, business, scenario
from .utils import business_fields
from .webhook import webhook

super_hub = APIRouter()


@super_hub.get("/")
def read_main():
    return {"msg": "Hello World"}


super_hub.include_router(login.router, prefix="/auth", tags=["auth"])
super_hub.include_router(logout.router, prefix="/auth", tags=["auth"])
super_hub.include_router(signup.router, prefix="/auth", tags=["auth"])
super_hub.include_router(token.router, prefix="/auth", tags=["auth"])

super_hub.include_router(legacy.router, prefix="/model", tags=["model"])

super_hub.include_router(information.router, prefix="/user", tags=["user"])
super_hub.include_router(business.router, prefix="/user", tags=["user"])
super_hub.include_router(scenario.router, prefix="/user", tags=["user"])

super_hub.include_router(business_fields.router, prefix="/utils", tags=["utils"])

super_hub.include_router(webhook.router)