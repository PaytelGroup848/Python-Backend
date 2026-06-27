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
    
    async def update(

        self,

        db: AsyncSession,

        promotion: ModelPromotion

    ):

        await db.flush()

        await db.refresh(
            promotion
        )

        return promotion
    
    async def delete(

        self,

        db: AsyncSession,

        promotion: ModelPromotion

    ):

        await db.delete(
            promotion
        )

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
    
    async def get_latest(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                ModelPromotion
            )

            .order_by(
                ModelPromotion.created_at.desc()
            )

            .limit(1)

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

            .order_by(
                ModelPromotion.created_at.desc()
            )

        )

        return result.scalars().all()
    
    async def list_by_status(

        self,

        db: AsyncSession,

        promotion_status: str

    ):

        result = await db.execute(

            select(
                ModelPromotion
            )

            .where(
                ModelPromotion.promotion_status
                ==
                promotion_status
            )

            .order_by(
                ModelPromotion.created_at.desc()
            )

        )

        return result.scalars().all()
    
    async def list_by_environment(

        self,

        db: AsyncSession,

        target_environment: str

    ):

        result = await db.execute(

            select(
                ModelPromotion
            )

            .where(
                ModelPromotion.target_environment
                ==
                target_environment
            )

            .order_by(
                ModelPromotion.created_at.desc()
            )

        )

        return result.scalars().all()


model_promotion_repository = (
    ModelPromotionRepository()
)