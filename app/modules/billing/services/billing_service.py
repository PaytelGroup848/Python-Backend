from app.modules.billing.repositories.billing_repository import (
    billing_repository
)


class BillingService:

    MODEL_PRICING = {

        "gpt-4o":
            0.005,

        "gpt-4o-mini":
            0.00015,

        "llama-3.1-8b-instant":
            0.0002,

        "gemini-2.5-flash":
            0.0003,

        "mistral-small":
            0.0002,

        "deepseek-v3":
            0.00015
    }

    def calculate_cost(
        self,
        model_name,
        tokens
    ):

        price = (
            self.MODEL_PRICING
            .get(
                model_name,
                0.0002
            )
        )

        return round(

            (
                tokens / 1000
            ) * price,

            6
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

            cost = (
                self.calculate_cost(

                    row.model_name,

                    row.tokens or 0
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