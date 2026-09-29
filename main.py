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


# async def get_current_user_websocket(
#     websocket: WebSocket,
#     session: AsyncSession = Depends(db_helper.session_dependency),
# ) -> User:
#     # Достаем токен из query параметров
#     token = websocket.query_params.get("token")
#     if not token:
#         # Если токена нет, кидаем HTTPException (FastAPI закроет соединение)
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token missing")
    
#     users = UserRepository(session)
#     service = AuthService(users)
    
#     try:
#         current_user = await service.verify_token(token)
#         if not current_user:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found")
#         return current_user
#     except Exception:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

# @app.websocket("/ws")
# async def websocket_endpoint(
#     websocket: WebSocket,
#     session: AsyncSession = Depends(db_helper.session_dependency),
# ):
#     # 1. ОБЯЗАТЕЛЬНО принимаем хендшейк первыми
#     await websocket.accept() 

#     users = UserRepository(session)
#     service = AuthService(users)

#     token = websocket.query_params.get("token")

#     # 2. Если токена нет — закрываем с кодом 1008
#     if not token:
#         await websocket.close(code=1007)
#         return

#     try:
#         current_user = await service.verify_token(token)
#         # Если токен расшифрован, но юзер в БД не найден
#         if not current_user:
#             await websocket.close(code=1008)
#             return
#     except Exception:
#         # 3. Если JWT невалиден или просрочен
#         await websocket.close(code=1009)
#         return

#     # Если всё ок, регистрируем в менеджере
#     await manager.connect(current_user, websocket)

#     try:
#         while True:
#             data = await websocket.receive_text()
#             print(f"{current_user.id}: {data} Онлайн")

#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(
#             f"Клиент {current_user.id} покинул чат"
#         )

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


if __name__ == "__main__":
    uvicorn.run("main:app")