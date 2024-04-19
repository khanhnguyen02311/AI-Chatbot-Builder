from fastapi import FastAPI, WebSocket, APIRouter

router = APIRouter(prefix="ws")


@router.websocket("")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
