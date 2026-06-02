from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.repositories.user_repository import (
    UserRepository
)


class UserService:

    def __init__(self):

        self.repository = (
            UserRepository()
        )

    async def get_users(
        self,
        db: AsyncSession
    ):

        users = await (
            self.repository
            .get_users(db)
        )

        return {
            "users": users
        }