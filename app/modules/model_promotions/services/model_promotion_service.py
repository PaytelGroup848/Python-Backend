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

        return await (
            model_promotion_repository
            .create(
                db,
                promotion
            )
        )

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


model_promotion_service = (
    ModelPromotionService()
)