import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from configurations.envs import General
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models.postgres import Account
from components.data.schemas import bot as BotSchemas
from components.data.schemas import bot_context as BotContextSchemas
from components.services.account import AccountService
from components.services.bot import BotService

router = APIRouter(prefix="/bots")


@router.get("")
def get_all_bots(account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bots = bot_service.get_account_bots(account)
        return BotSchemas.ListBotFULL.model_validate(bots)


@router.post("")
def create_bot(data: BotSchemas.BotPOST, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        new_bot = bot_service.create_new_bot(data, account)
        if new_bot is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bot creation failed")
        session.commit()
        return BotSchemas.BotFULL.model_validate(new_bot)


@router.get("/{bot_id}")
def get_bot(bot_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bot = bot_service.validate_account_bot(bot_id, account.id)
        if bot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
        return BotSchemas.BotFULL.model_validate(bot)


@router.put("/{bot_id}")
def update_bot(bot_id: int, data: BotSchemas.BotPUT, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        updated_bot = bot_service.update_account_bot(bot_id, data, account)
        if updated_bot is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bot update failed")
        session.commit()
        return BotSchemas.BotFULL.model_validate(updated_bot)


@router.delete("/{bot_id}")
def delete_bot(bot_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bot_service.delete_account_bot(bot_id, account)
        session.commit()
    return {"message": "Bot deleted"}


@router.get("/{bot_id}/contexts")
def get_bot_contexts(bot_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        contexts = bot_service.get_bot_contexts(bot_id, account)
        return BotContextSchemas.ListBotContextFULL.model_validate(contexts)


@router.post("/{bot_id}/contexts")
async def add_bot_context(bot_id: int, file: UploadFile, account: Account = Depends(AccountService.validate_token)):
    if file.content_type not in General.BOT_CONTEXT_ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type, only txt/pdf/doc/docx files allowed")
    file.filename = f"{bot_id}_{int(datetime.now(timezone.utc).timestamp())}_{file.filename}"

    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        bot_context = bot_service.create_new_bot_context(BotContextSchemas.BotContextPOST(filename=file.filename, id_bot=bot_id), account)
        with open(f"{os.path.join(General.BOT_CONTEXT_FILE_LOCATION, file.filename)}", "wb+") as f:
            try:
                f.write(file.file.read())
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        session.commit()
        return BotContextSchemas.BotContextFULL.model_validate(bot_context)
    # TODO: additional step to load to vector dbs


@router.get("/{bot_id}/contexts/{context_id}")
def get_bot_context_file(bot_id: int, context_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        context = bot_service.get_bot_context(bot_id, context_id, account)
        if context is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot context not found")

        if not os.path.exists(os.path.join(General.BOT_CONTEXT_FILE_LOCATION, context.filename)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot context's file data not found")

        return FileResponse(f"{os.path.join(General.BOT_CONTEXT_FILE_LOCATION, context.filename)}")


@router.delete("/{bot_id}/contexts/{context_id}")
async def delete_bot_context(bot_id: int, context_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        bot_service = BotService(session=session)
        deleted_bot_context = bot_service.delete_bot_context(context_id, account)
        os.remove(f"{os.path.join(General.BOT_CONTEXT_FILE_LOCATION, deleted_bot_context.filename)}")
        session.commit()
    return {"message": "Bot context deleted"}
    # TODO: additional step to remove from vector dbs
