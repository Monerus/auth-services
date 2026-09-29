from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.users_repository import *
from app.database import db_helper
from app.service.auth import *
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.redis import get_redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/verify-code/")


def get_user_repository(session: AsyncSession = Depends(db_helper.session_dependency)) -> UserRepository:
    return UserRepository

def get_redis_auth(redis=Depends(get_redis)) -> RedisAuth:
    return RedisAuth(redis)

def get_auth_service(users: UserRepository = Depends(get_user_repository),
                    #  code: RedisAuth = Depends(get_redis_auth)
                     ) -> AuthService:
    return AuthService(users,) #code)

async def get_current_user(auth_service: AuthService = Depends(get_auth_service),
                           token: Annotated[str, Depends(oauth2_scheme)] = None) -> User:
    return await auth_service.get_current_user(token)



