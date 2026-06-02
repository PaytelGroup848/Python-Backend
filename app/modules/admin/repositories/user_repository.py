from sqlalchemy import (
    select,
    func
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.models.user import User

from app.models.token_usage import (
    TokenUsage
)


class UserRepository:

    async def get_users(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(

                User,

                func.coalesce(
                    func.sum(
                        TokenUsage.total_tokens
                    ),
                    0
                ).label(
                    "total_tokens"
                )

            )

            .outerjoin(
                TokenUsage,
                User.id == TokenUsage.user_id
            )

            .group_by(
                User.id
            )
        )

        rows = result.all()

        users = []

        for user, total_tokens in rows:

            user.total_tokens = (
                total_tokens
            )

            user.remaining_tokens = max(
                0,
                user.token_limit - total_tokens
            )

            users.append(user)

        return users

    async def get_by_id(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()