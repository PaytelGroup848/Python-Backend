from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:

    async def get_users(
        self,
        db: AsyncSession
    ):

        result = await db.execute(
            select(User)
        )

        return result.scalars().all()