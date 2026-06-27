from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.model_promotions.models.model_promotion import (
    ModelPromotion
)

from app.modules.model_promotions.repositories.model_promotion_repository import (
    model_promotion_repository
)

from app.modules.model_promotions.schemas.model_promotion_create import (
    ModelPromotionCreate
)


class ModelPromotionService:

    async def create_promotion(

        self,

        db: AsyncSession,

        data: ModelPromotionCreate

    ):

        promotion = ModelPromotion(
            **data.model_dump()
        )

        promotion = await (
            model_promotion_repository
            .create(
                db=db,
                promotion=promotion
            )
        )

        return promotion

    async def get_promotion(

        self,

        db: AsyncSession,

        promotion_id: int

    ):

        return await (
            model_promotion_repository
            .get_by_id(
                db,
                promotion_id
            )
        )
    
    async def list_promotions(

        self,

        db: AsyncSession

    ):

        return await (
            model_promotion_repository
            .list_all(
                db=db
            )
        )
    
    async def list_promotions_by_status(

        self,

        db: AsyncSession,

        promotion_status: str

    ):

        return await (
            model_promotion_repository
            .list_by_status(
                db=db,
                promotion_status=promotion_status
            )
        )
    
    async def list_promotions_by_environment(

        self,

        db: AsyncSession,

        target_environment: str

    ):

        return await (
            model_promotion_repository
            .list_by_environment(
                db=db,
                target_environment=target_environment
            )
        )
    
    async def get_latest_promotion(

        self,

        db: AsyncSession

    ):

        return await (
            model_promotion_repository
            .get_latest(
                db=db
            )
        )
    
    async def update_promotion(

        self,

        db: AsyncSession,

        promotion: ModelPromotion

    ):

        return await (
            model_promotion_repository
            .update(
                db=db,
                promotion=promotion
            )
        )
    
    async def delete_promotion(

        self,

        db: AsyncSession,

        promotion_id: int

    ) -> bool:

        promotion = await (
            model_promotion_repository
            .get_by_id(
                db=db,
                promotion_id=promotion_id
            )
        )

        if promotion is None:

            return False

        await (
            model_promotion_repository
            .delete(
                db=db,
                promotion=promotion
            )
        )

        return True


model_promotion_service = (
    ModelPromotionService()
)