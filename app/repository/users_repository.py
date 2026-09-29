from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import *
from sqlalchemy import select 
from app.models.auth import User 


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    #1. Ищет пользователя по почте
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    #2. Записывает пользователя.
    async def create(self, email: str) -> User: 
        user = User(email = email)
        self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_by_id(self, id: bytes | str):
        result = await self.session.execute(
            select(User).where(User.id == id)
        )

        return result.scalars().first()