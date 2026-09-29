import secrets
import bcrypt
from app.config import *

CODE_TTL = 300




class RedisAuth:
    def __init__(self, redis):
        self.redis = redis

    # def resend_key(self, email: str) -> str:
    #     return f"auth:resend:{email}"

    #1.Создаем ключ
    def code_key(self, email: str) -> str:
        return f"auth:code:{email}"

    #2.Генерация кода
    def generate_code(self) -> str:
        return f"{secrets.randbelow(1_000_000):06d}" 

    #3.Сохраняем ключ + код
    async def save_code(self, email: str, hashed_code: bytes):
        await self.redis.set(
            self.code_key(email),
            hashed_code,
            ex=CODE_TTL
        )

    #4.Достаем ключ + код
    async def get_code(
        self,
        email: str,
    ) -> bytes | None:

        code = await self.redis.get(
            self.code_key(email)
        )

        return code


    #7. Удаляем код
    async def delete_code(self, email: str):
        await self.redis.delete(self.code_key(email))

    # 5. Закешировать код, который пришел на почту.
    def hash_code(self, code: str) -> bytes:
        return bcrypt.hashpw(code.encode(), 
                             bcrypt.gensalt())

    # 6. Проверка кода закешированного с тем, что пришло в редис.
    def hash_verify_code(
        self,
        code: str,
        hashed_code: str | bytes,
    ) -> bool:

        if isinstance(hashed_code, str):
            hashed_code = hashed_code.encode()

        return bcrypt.checkpw(
            code.encode(),
            hashed_code,
        )


    


     