from decimal import Decimal

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
        model_name: str
    ):

        return await (
            pricing_repository.get_by_model(
                db,
                model_name
            )
        )

    async def get_active_pricing(
        self,
        db,
        model_name: str
    ):

        pricing = await (
            pricing_repository
            .get_active_pricing(
                db,
                model_name
            )
        )

        if not pricing:

            raise Exception(
                f"No active pricing found "
                f"for model: {model_name}"
            )

        return pricing

    async def calculate_cost(
        self,
        db,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int
    ):

        pricing = await (
            self.get_active_pricing(
                db,
                model_name
            )
        )

        prompt_cost = (

            Decimal(prompt_tokens)
            / Decimal("1000")

        ) * Decimal(
            str(
                pricing.input_cost_per_1k
            )
        )

        completion_cost = (

            Decimal(completion_tokens)
            / Decimal("1000")

        ) * Decimal(
            str(
                pricing.output_cost_per_1k
            )
        )

        total_cost = (
            prompt_cost
            + completion_cost
        )

        return {

            "pricing":
                pricing,

            "model_name":
                model_name,

            "provider":
                pricing.provider,

            "prompt_tokens":
                prompt_tokens,

            "completion_tokens":
                completion_tokens,

            "prompt_cost":
                prompt_cost,

            "completion_cost":
                completion_cost,

            "total_cost":
                total_cost
        }

    async def estimate_cost(
        self,
        db,
        model_name: str,
        tokens: int
    ):

        pricing = await (
            self.get_active_pricing(
                db,
                model_name
            )
        )

        estimated_cost = (

            Decimal(tokens)
            / Decimal("1000")

        ) * Decimal(
            str(
                pricing.input_cost_per_1k
            )
        )

        return {

            "model_name":
                model_name,

            "provider":
                pricing.provider,

            "tokens":
                tokens,

            "estimated_cost":
                estimated_cost
        }


pricing_service = (
    PricingService()
)