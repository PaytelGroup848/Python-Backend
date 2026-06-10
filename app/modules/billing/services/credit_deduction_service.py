
from app.modules.billing.services.wallet_service import (
    wallet_service
)
from app.modules.pricing.services.pricing_service import (
    pricing_service
)

class CreditDeductionService:

    async def deduct(
        self,
        db,
        user_id: int,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        reference_id: str = None
    ):

        cost_data = await (
            pricing_service.calculate_cost(
                db=db,
                model_name=model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens
            )
        )

        total_cost = cost_data[
            "total_cost"
        ]

        if total_cost <= 0:

            return {

                "model_name":
                    model_name,

                "prompt_tokens":
                    prompt_tokens,

                "completion_tokens":
                    completion_tokens,

                "prompt_cost":
                    0,

                "completion_cost":
                    0,

                "cost":
                    0
            }

        await wallet_service.debit_wallet(

            db=db,

            user_id=user_id,

            amount=total_cost,

            description=(
                f"AI usage charge "
                f"({model_name})"
            ),

            reference_type="api_request",

            reference_id=(
                str(reference_id)
                if reference_id
                else None
            )
        )

        return {

            "model_name":
                model_name,

            "prompt_tokens":
                prompt_tokens,

            "completion_tokens":
                completion_tokens,

            "prompt_cost":
                float(
                    cost_data[
                        "prompt_cost"
                    ]
                ),

            "completion_cost":
                float(
                    cost_data[
                        "completion_cost"
                    ]
                ),

            "cost":
                float(total_cost)
        }


credit_deduction_service = (
    CreditDeductionService()
)