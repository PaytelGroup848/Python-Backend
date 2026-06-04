from app.modules.usage.repositories.usage_repository import (
    usage_repository
)


class UsageService:

    async def get_usage_overview(
        self,
        db
    ):

        totals = await (
            usage_repository
            .get_overview(db)
        )

        top_models = await (
            usage_repository
            .top_models(db)
        )

        top_users = await (
            usage_repository
            .top_users(db)
        )

        total_tokens = int(

            totals[0] or 0
        )

        prompt_tokens = int(

            totals[1] or 0
        )

        completion_tokens = int(

            totals[2] or 0
        )

        estimated_cost = round(

            (
                total_tokens
                / 1000
            ) * 0.002,

            6
        )

        return {

            "total_tokens":
                total_tokens,

            "prompt_tokens":
                prompt_tokens,

            "completion_tokens":
                completion_tokens,

            "estimated_cost":
                estimated_cost,

            "top_models": [

                {

                    "model_name":
                        row.model_name,

                    "tokens":
                        int(row.tokens or 0)
                }

                for row
                in top_models
            ],

            "top_users": [

                {

                    "user_id":
                        row.user_id,

                    "tokens":
                        int(row.tokens or 0)
                }

                for row
                in top_users
            ]
        }


usage_service = (
    UsageService()
)