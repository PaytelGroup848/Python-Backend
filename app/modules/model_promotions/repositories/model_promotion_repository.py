from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.model_promotions.models.model_promotion import (
    ModelPromotion
)


class ModelPromotionRepository:

    async def create(

        self,

        db: AsyncSession,

        promotion: ModelPromotion

    ):

        db.add(
            promotion
        )

        await db.flush()

        await db.refresh(
            promotion
        )

        return promotion

    async def get_by_id(

        self,

        db: AsyncSession,

        promotion_id: int

    ):

        result = await db.execute(

            select(
                ModelPromotion
            )
            .where(
                ModelPromotion.id
                ==
                promotion_id
            )
        )

        return result.scalar_one_or_none()

    async def list_all(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                ModelPromotion
            )
        )

        return result.scalars().all()


model_promotion_repository = (
    ModelPromotionRepository()
)