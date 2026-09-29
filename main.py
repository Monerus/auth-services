from fastapi import FastAPI
from fastapi import APIRouter, Depends, WebSocket, status, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as user_router
from sqlalchemy.ext.asyncio import AsyncSession
from app.service.websocket import *
from app.database import db_helper
# from app.dependency import get_current_user
import json
import logging

logger = logging.getLogger(__name__)

# Клиент (WebSocketContext.jsx) не переподключается при этом коде
WS_AUTH_FAILED = 4401

from app.service.auth import *
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)


async def authenticate_websocket(websocket: WebSocket) -> User | None:
    """Возвращает пользователя по токену из query или None."""
    token = websocket.query_params.get("token")

    if not token:
        return None

    # Сессия БД нужна только на время проверки токена,
    # а не на всё время жизни соединения.
    # Замените на ваш способ получить сессию вне Depends
    # (например, db_helper.session_factory()).
    async with db_helper.session_factory() as session:
        service = AuthService(UserRepository(session))

        try:
            return await service.verify_token(token)
        except Exception:
            return None


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Сначала принимаем рукопожатие, иначе браузер увидит только код 1006
    # и не узнает причину закрытия
    await websocket.accept()

    current_user = await authenticate_websocket(websocket)

    if current_user is None:
        await websocket.close(code=WS_AUTH_FAILED, reason="Unauthorized")
        return

    await manager.connect(current_user, websocket)

    try:
        while True:
            data = await websocket.receive_text()

            # Необязательный keep-alive: {"type": "ping"} -> {"type": "pong"}
            try:
                payload = json.loads(data)
            except ValueError:
                continue

            if isinstance(payload, dict) and payload.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info("WebSocket: пользователь %s отключился", current_user.id)

    finally:
        manager.disconnect(websocket)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(user_router)


# if __name__ == "__main__":
#     uvicorn.run("main:app")