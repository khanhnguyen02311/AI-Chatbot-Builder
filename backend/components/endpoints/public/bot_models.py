from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from components.data import POSTGRES_SESSION_FACTORY

router = APIRouter()


@router.get("/bot-models")
async def get_bot_model_names():
    return ["gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-4-turbo"]
