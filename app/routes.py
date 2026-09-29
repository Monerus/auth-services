from fastapi import APIRouter, Depends, WebSocket
from app.schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_helper
from app.schemas.auth import *
from app.service.auth import *
from app.repository.users_repository import *
from app.service.token import *
from app.service.redis import *
from app.redis import *
from fastapi.security import OAuth2PasswordBearer
from app.dependency import get_current_user
from app.service.websocket import *
router = APIRouter(prefix="/user", tags=["User"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/verify-code/")


#создание аккаунта + временный код на почту.
@router.post("/login/", 
             response_model=UserResponse)
async def register(user_in: UserBase,
                #    redis: Redis = Depends(get_redis),
                   session: AsyncSession = Depends(db_helper.session_dependency)
                   ):


    # redis_auth = RedisAuth(redis)
    users = UserRepository(session)
    service = AuthService(users,) #redis_auth)

    #code / tut
    user = await service.register(user_in.email)

    return UserResponse(
        id=user.id,
        email=user.email,
        # code=code
    )



#ручка, проверяет почту и код + выдает токены
@router.post(
    "/verify-code/",
    response_model=Token,
)
async def verify_code(
    user_in: VerifyCode,
    # redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(
        db_helper.session_dependency
    ),
):

    users = UserRepository(session)

    # redis_auth = RedisAuth(redis)

    service = AuthService(
        users,
        # redis_auth,
    )

    user = await service.verify_code(
        email=user_in.email,
        # code=user_in.code,
    )

    token_service = TokenService()

    access_token = token_service.create_access_token(
        user
    )

    refresh_token = token_service.create_refresh_token(
        user
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/test/")
async def test_post(
    session: AsyncSession = Depends(db_helper.session_dependency),
    token: str = Depends(oauth2_scheme)
): 

    users = UserRepository(session)

    redis_auth = RedisAuth(redis)

    auth_service = AuthService(users, redis_auth)

    current_user = await auth_service.get_current_user(token)

    return current_user

#ДОДЕЛАТЬ!
@router.post("/refresh/")
async def refresh_auth(): pass



@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket,
                             session: AsyncSession = Depends(db_helper.session_dependency),
                             current_user: str = "593e8586-f56a-45db-8a47-a024597cdeb5"):
    await manager.connect(websocket, current_user)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"{data}")
            await manager.broadcast(f"Написал: {current_user}, {data}")
            print("Мы в сети")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{current_user} left the chat")