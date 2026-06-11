from sqlalchemy import (
    select,
    desc
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.plan_version import (
    PlanVersion
)


class PlanVersionRepository:

    async def create(
        self,
        db: AsyncSession,
        plan_version: PlanVersion
    ):

        try:

            db.add(
                plan_version
            )

            await db.commit()

            await db.refresh(
                plan_version
            )

            return (
                plan_version
            )

        except Exception:

            await db.rollback()

            raise

    async def get_by_id(
        self,
        db: AsyncSession,
        version_id: int
    ):

        result = await db.execute(

            select(
                PlanVersion
            )

            .where(
                PlanVersion.id
                == version_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_active_by_plan(
        self,
        db: AsyncSession,
        plan_id: int
    ):

        result = await db.execute(

            select(
                PlanVersion
            )

            .where(
                PlanVersion.plan_id
                == plan_id
            )

            .where(
                PlanVersion.is_active
                == True
            )

            .order_by(
                desc(
                    PlanVersion.version_number
                )
            )
        )

        return (
            result.scalars()
            .first()
        )

    async def get_latest_version(
        self,
        db: AsyncSession,
        plan_id: int
    ):

        result = await db.execute(

            select(
                PlanVersion
            )

            .where(
                PlanVersion.plan_id
                == plan_id
            )

            .order_by(
                desc(
                    PlanVersion.version_number
                )
            )
        )

        return (
            result.scalars()
            .first()
        )

    async def get_versions_by_plan(
        self,
        db: AsyncSession,
        plan_id: int
    ):

        result = await db.execute(

            select(
                PlanVersion
            )

            .where(
                PlanVersion.plan_id
                == plan_id
            )

            .order_by(
                desc(
                    PlanVersion.version_number
                )
            )
        )

        return (
            result.scalars()
            .all()
        )

    async def update(
        self,
        db: AsyncSession,
        plan_version: PlanVersion
    ):

        try:

            await db.commit()

            await db.refresh(
                plan_version
            )

            return (
                plan_version
            )

        except Exception:

            await db.rollback()

            raise

    async def delete(
        self,
        db: AsyncSession,
        plan_version: PlanVersion
    ):

        await db.delete(
            plan_version
        )

        await db.commit()


plan_version_repository = (
    PlanVersionRepository()
)