from app.models.model_pricing import (
    ModelPricing
)

from app.modules.pricing.repositories.pricing_repository import (
    pricing_repository
)


class PricingService:

    async def create_pricing(
        self,
        db,
        payload
    ):

        pricing = ModelPricing(

            model_name=
            payload.model_name,

            provider=
            payload.provider,

            input_cost_per_1k=
            payload.input_cost_per_1k,

            output_cost_per_1k=
            payload.output_cost_per_1k
        )

        return await (
            pricing_repository.create(
                db,
                pricing
            )
        )

    async def get_all_pricing(
        self,
        db
    ):

        return await (
            pricing_repository.get_all(
                db
            )
        )

    async def get_model_pricing(
        self,
        db,
        model_name
    ):

        return await (
            pricing_repository.get_by_model(
                db,
                model_name
            )
        )


pricing_service = (
    PricingService()
)