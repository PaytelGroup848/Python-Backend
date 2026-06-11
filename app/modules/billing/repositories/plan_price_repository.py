from sqlalchemy import (
    select
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.plan_price import (
    PlanPrice
)


class PlanPriceRepository:

    async def create(
        self,
        db: AsyncSession,
        plan_price: PlanPrice
    ):

        try:

            db.add(
                plan_price
            )

            await db.commit()

            await db.refresh(
                plan_price
            )

            return (
                plan_price
            )

        except Exception:

            await db.rollback()

            raise

    async def get_by_id(
        self,
        db: AsyncSession,
        price_id: int
    ):

        result = await db.execute(

            select(
                PlanPrice
            )

            .where(
                PlanPrice.id
                == price_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_active_price(
        self,
        db: AsyncSession,
        plan_version_id: int,
        provider: str,
        billing_cycle: str,
        currency: str
    ):

        result = await db.execute(

            select(
                PlanPrice
            )

            .where(
                PlanPrice.plan_version_id
                == plan_version_id
            )

            .where(
                PlanPrice.provider
                == provider
            )

            .where(
                PlanPrice.billing_cycle
                == billing_cycle
            )

            .where(
                PlanPrice.currency
                == currency
            )

            .where(
                PlanPrice.is_active
                == True
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_plan_prices(
        self,
        db: AsyncSession,
        plan_version_id: int
    ):

        result = await db.execute(

            select(
                PlanPrice
            )

            .where(
                PlanPrice.plan_version_id
                == plan_version_id
            )
        )

        return (
            result.scalars()
            .all()
        )

    async def get_provider_prices(
        self,
        db: AsyncSession,
        provider: str
    ):

        result = await db.execute(

            select(
                PlanPrice
            )

            .where(
                PlanPrice.provider
                == provider
            )

            .where(
                PlanPrice.is_active
                == True
            )
        )

        return (
            result.scalars()
            .all()
        )
    
    async def get_by_external_price_id(
        self,
        db: AsyncSession,
        provider: str,
        external_price_id: str
    ):
        result = await db.execute(

            select(
                PlanPrice
            )

            .where(
                PlanPrice.provider
                == provider
            )

            .where(
                PlanPrice.external_price_id
                == external_price_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def update(
        self,
        db: AsyncSession,
        plan_price: PlanPrice
    ):

        try:

            await db.commit()

            await db.refresh(
                plan_price
            )

            return (
                plan_price
            )

        except Exception:

            await db.rollback()

            raise

    async def delete(
        self,
        db: AsyncSession,
        plan_price: PlanPrice
    ):

        await db.delete(
            plan_price
        )

        await db.commit()


plan_price_repository = (
    PlanPriceRepository()
)