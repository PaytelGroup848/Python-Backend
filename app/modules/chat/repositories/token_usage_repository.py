from sqlalchemy import (
    select,
    func
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.models.token_usage import (
    TokenUsage
)


class TokenUsageRepository:

    async def create(
        self,
        db: AsyncSession,
        usage: TokenUsage
    ):

        db.add(usage)

        await db.commit()

        await db.refresh(usage)

        return usage

    async def get_total_tokens(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(

                func.coalesce(

                    func.sum(
                        TokenUsage.total_tokens
                    ),

                    0

                )

            ).where(

                TokenUsage.user_id == user_id

            )
        )

        return result.scalar() or 0