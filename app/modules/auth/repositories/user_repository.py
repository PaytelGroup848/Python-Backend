
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(
    BaseRepository[User]
):

    def __init__(self):

        super().__init__(
            User
        )

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ):

        result = await db.execute(

            select(User)

            .where(
                User.email == email
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_by_id(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(User)

            .where(
                User.id == user_id
            )
        )

        return (
            result.scalar_one_or_none()
        )
    
user_repository = (
    UserRepository()
)