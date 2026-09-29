from app.repository.users_repository import *
from app.schemas.auth import *
from fastapi import HTTPException, Depends 
from app.service.redis import *
import secrets
import jwt

class AuthService:

    def __init__(self, users: UserRepository): #code: Redis):
        self.users = users
        # self.code = code


    async def register(self, email: str):

        existing_user = await self.users.get_by_email(email)

        if existing_user :
            raise HTTPException(
                status_code=409,
                detail="Пользователь уже существует",
            )


        # random_code = self.code.generate_code()
        # hashed_code = self.code.hash_code(random_code)

        user = await self.users.create(email)

        # await self.code.save_code(
        #     email,
        #     # hashed_code
        # )

        return user, #random_code
    
    async def verify_code(
        self,
        email: str,
        # code: str,
    ):

        existing_user = await self.users.get_by_email(
            email
        )

        if not existing_user:
            raise HTTPException(
                status_code=401,
                detail="Неверные данные",
            )

        # saved_code = await self.code.get_code(
        #     email
        # )

        # if not saved_code:
        #     raise HTTPException(
        #         status_code=401,
        #         detail="Код истёк или не существует",
        #     )

        # is_valid = self.code.hash_verify_code(
        #     code,
        #     saved_code,
        # )

        # if not is_valid:
        #     raise HTTPException(
        #         status_code=401,
        #         detail="Неверный код",
        #     )

        # await self.code.delete_code(email)

        return existing_user


    async def get_current_user(self,
                               token: str) -> User:

        try:
            payload = jwt.decode(token, 
                                 settings.JWT_SECRET, 
                                 algorithms=[settings.JWT_ALGORITHM])

        except jwt.PyJWTError:
            raise HTTPException(
                status_code=401,
                detail="Неверный токен или умер"
            )
        
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Ошибка с пользователем")

        existing_user = await self.users.get_by_id(user_id)

        if existing_user is None:

            raise HTTPException(
                status_code=401,
                detail="Пользователь не найден",
            )

        return existing_user


    async def verify_token(self, token: str):
        payload = jwt.decode(token, 
                             settings.PUBLIC_KEY_PATH.read_text(),
                             algorithms=[settings.JWT_ALGORITHM])

        user_id = payload.get("sub")

        user = await self.users.get_by_id(user_id)

        return user
        

        

    

    




