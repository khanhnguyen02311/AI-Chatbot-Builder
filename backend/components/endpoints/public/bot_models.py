from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from configurations.envs import ChatModels

router = APIRouter()


@router.get("/bot-models")
async def get_bot_model_names():
    return ChatModels.ALLOWED_LLM_MODEL_NAMES
