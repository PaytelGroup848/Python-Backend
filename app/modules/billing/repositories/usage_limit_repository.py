from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.usage_limit import (
    UsageLimit
)


class UsageLimitRepository:

    async def create(
        self,
        db: AsyncSession,
        usage_limit: UsageLimit
    ):

        db.add(
            usage_limit
        )

        await db.commit()

        await db.refresh(
            usage_limit
        )

        return usage_limit

    async def get_by_plan(
        self,
        db: AsyncSession,
        plan_name: str
    ):

        result = await db.execute(

            select(
                UsageLimit
            )

            .where(
                UsageLimit.plan_name
                == plan_name
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_all(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(
                UsageLimit
            )
        )

        return (
            result.scalars()
            .all()
        )

    async def update(
        self,
        db: AsyncSession,
        usage_limit: UsageLimit
    ):

        await db.commit()

        await db.refresh(
            usage_limit
        )

        return usage_limit


usage_limit_repository = (
    UsageLimitRepository()
)