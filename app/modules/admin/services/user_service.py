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
    
    async def update_user_plan(
        self,
        db: AsyncSession,
        user_id: int,
        plan_name: str
    ):

        PLAN_LIMITS = {

            "free":
                1_000_000,

            "pro":
                20_000_000,

            "business":
                100_000_000,

            "enterprise":
                9_999_999_999
        }

        plan_name = (
            plan_name.lower()
        )

        if plan_name not in PLAN_LIMITS:

            raise ValueError(
                "Invalid plan"
            )

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

        user.plan_name = (
            plan_name
        )

        user.token_limit = (
            PLAN_LIMITS[
                plan_name
            ]
        )

        await db.commit()

        await db.refresh(user)

        return {

            "message":
                "Plan updated successfully",

            "user_id":
                user.id,

            "plan_name":
                user.plan_name,

            "token_limit":
                user.token_limit
        }