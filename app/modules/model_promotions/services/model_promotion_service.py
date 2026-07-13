from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from datetime import datetime

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
        existing_promotion = await (

            model_promotion_repository

            .get_by_release(

                db=db,

                release_id=data.release_id,

            )

        )

        if existing_promotion is not None:

            raise ValueError(

                "Promotion already exists "

                "for this release."

            )

        promotion = ModelPromotion(

            evaluation_job_id=
                data.evaluation_job_id,

            release_id=
                data.release_id,

            promotion_status=
                data.promotion_status,

            target_environment=
                data.target_environment,

            is_active=
                data.is_active,

            approved_by=
                data.approved_by,

            approved_at=
                data.approved_at,

            approval_reason=
                data.approval_reason,
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
    
    async def approve_promotion(

        self,

        db: AsyncSession,

        promotion_id: int,

        approved_by: str,

        approval_reason: str | None = None,

    ):

        promotion = await (

            model_promotion_repository

            .get_by_id(

                db=db,

                promotion_id=promotion_id,

            )

        )

        if promotion is None:

            raise ValueError(

                "Promotion not found."

            )

        promotion.promotion_status = (

            "APPROVED"

        )

        promotion.approved_by = (

            approved_by

        )

        promotion.approved_at = (

            datetime.utcnow()

        )

        promotion.approval_reason = (

            approval_reason

        )

        return await (

            model_promotion_repository

            .update(

                db=db,

                promotion=promotion,

            )

        )
    
    async def reject_promotion(

        self,

        db: AsyncSession,

        promotion_id: int,

        approved_by: str,

        approval_reason: str,

    ):

        promotion = await (

            model_promotion_repository

            .get_by_id(

                db=db,

                promotion_id=promotion_id,

            )

        )

        if promotion is None:

            raise ValueError(

                "Promotion not found."

            )

        promotion.promotion_status = (

            "REJECTED"

        )

        promotion.approved_by = (

            approved_by

        )

        promotion.approved_at = (

            datetime.utcnow()

        )

        promotion.approval_reason = (

            approval_reason

        )

        return await (

            model_promotion_repository

            .update(

                db=db,

                promotion=promotion,

            )

        )
    
    async def archive_promotion(

        self,

        db: AsyncSession,

        promotion_id: int,

    ):

        promotion = await (

            model_promotion_repository

            .get_by_id(

                db=db,

                promotion_id=promotion_id,

            )

        )

        if promotion is None:

            raise ValueError(

                "Promotion not found."

            )

        promotion.promotion_status = (

            "ARCHIVED"

        )

        return await (

            model_promotion_repository

            .update(

                db=db,

                promotion=promotion,

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