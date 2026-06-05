from sqlalchemy import (
    select
)

from app.models.model_pricing import (
    ModelPricing
)


class PricingRepository:

    async def create(
        self,
        db,
        pricing
    ):

        db.add(
            pricing
        )

        await db.commit()

        await db.refresh(
            pricing
        )

        return pricing

    async def get_all(
        self,
        db
    ):

        result = await db.execute(

            select(
                ModelPricing
            )
        )

        return (
            result.scalars()
            .all()
        )

    async def get_by_model(
        self,
        db,
        model_name: str
    ):

        result = await db.execute(

            select(
                ModelPricing
            )

            .where(
                ModelPricing.model_name
                == model_name
            )
        )

        return (
            result.scalar_one_or_none()
        )


pricing_repository = (
    PricingRepository()
)