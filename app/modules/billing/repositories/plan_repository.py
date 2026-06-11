from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.plan import (
    Plan
)


class PlanRepository:

    async def create(
        self,
        db: AsyncSession,
        plan: Plan
    ):

        try:

            db.add(plan)

            await db.commit()

            await db.refresh(plan)

            return plan

        except Exception:

            await db.rollback()

            raise

    async def get_by_id(
        self,
        db: AsyncSession,
        plan_id: int
    ):

        result = await db.execute(

            select(Plan)

            .where(
                Plan.id == plan_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_by_code(
        self,
        db: AsyncSession,
        plan_code: str
    ):

        result = await db.execute(

            select(Plan)

            .where(
                Plan.plan_code
                == plan_code
            )

            .where(
                Plan.is_active
                == True
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

            select(Plan)
        )

        return (
            result.scalars()
            .all()
        )

    async def get_public_plans(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(Plan)

            .where(
                Plan.is_public
                == True
            )

            .where(
                Plan.is_active
                == True
            )
        )

        return (
            result.scalars()
            .all()
        )

    async def update(
        self,
        db: AsyncSession,
        plan: Plan
    ):

        try:

            await db.commit()

            await db.refresh(plan)

            return plan

        except Exception:

            await db.rollback()

            raise


plan_repository = (
    PlanRepository()
)