from app.modules.billing.repositories.billing_repository import (
    billing_repository
)
from app.modules.pricing.repositories.pricing_repository import (
    pricing_repository
)

from decimal import Decimal


class BillingService:

    

    async def calculate_cost(
        self,
        db,
        model_name,
        prompt_tokens,
        completion_tokens
    ):

        pricing = await (
            pricing_repository
            .get_active_pricing(
                db,
                model_name
            )
        )

        if not pricing:

            return 0

        input_cost = (
            Decimal(str(prompt_tokens))
            / Decimal("1000")
        ) * Decimal(str(pricing.input_cost_per_1k))

        output_cost = (
            Decimal(str(completion_tokens))
            / Decimal("1000")
        ) * Decimal(str(pricing.output_cost_per_1k))

        return float(

            round(

                input_cost
                +
                output_cost,

                8
            )
        )

    async def get_billing_overview(
        self,
        db
    ):

        totals = await (
            billing_repository
            .get_global_usage(
                db
            )
        )

        providers = await (
            billing_repository
            .get_provider_usage(
                db
            )
        )

        models = await (
            billing_repository
            .get_model_usage(
                db
            )
        )

        total_requests = (
            totals[0]
        )

        total_tokens = (
            totals[1]
        )

        total_cost = 0

        model_breakdown = []

        for row in models:

            cost = await (
                self.calculate_cost(

                    db,

                    row.model_name,

                    row.prompt_tokens or 0,

                    row.completion_tokens or 0
                )
            )

            total_cost += cost

            model_breakdown.append({

                "model_name":
                    row.model_name,

                "requests":
                    row.requests,

                "tokens":
                    row.tokens,

                "cost":
                    cost
            })

        provider_breakdown = [

            {

                "provider":
                    row.provider,

                "requests":
                    row.requests,

                "tokens":
                    row.tokens
            }

            for row in providers
        ]

        return {

            "total_cost":
                round(
                    total_cost,
                    6
                ),

            "total_tokens":
                total_tokens,

            "total_requests":
                total_requests,

            "provider_breakdown":
                provider_breakdown,

            "model_breakdown":
                model_breakdown
        }


billing_service = (
    BillingService()
)