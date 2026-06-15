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

    async def update_user_status(
        self,
        db: AsyncSession,
        user_id: int,
        is_active: bool
    ):

        user = await (
            self.repository
            .get_by_id(
                db,
                user_id
            )
        )

        if not user:

            raise ValueError(
                "User not found"
            )

        user.is_active = is_active

        await db.commit()

        await db.refresh(user)

        return {
            "message":
                "User status updated",
            "user_id":
                user.id,
            "is_active":
                user.is_active
        }