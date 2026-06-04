from app.modules.analytics.repositories.analytics_repository import (
    analytics_repository
)


class AnalyticsService:

    async def overview(
        self,
        db
    ):

        total_requests = await (
            analytics_repository
            .total_requests(db)
        )

        avg_latency = await (
            analytics_repository
            .average_latency(db)
        )

        provider_stats = await (
            analytics_repository
            .requests_by_provider(db)
        )

        total_users = await (
            analytics_repository
            .total_users(db)
        )

        total_models = await (
            analytics_repository
        .total_models(db)
        )

        total_api_keys = await (
            analytics_repository
            .total_api_keys(db)
        )

        top_models = await (
            analytics_repository
            .top_models(db)
        )

        top_users = await (
            analytics_repository
            .top_users(db)
        )

        return {

            "total_requests":
                total_requests,

            "average_latency_ms":
                round(
                    avg_latency or 0,
                    2
                ),

            "total_users":
                total_users,

            "total_models":
                total_models,

            "total_api_keys":
                total_api_keys,

            "providers":
                [

                    {
                        "provider":
                            provider,

                        "requests":
                            count
                    }

                    for provider,
                    count
                    in provider_stats
                ],

            "top_models":
                [

                    {
                        "model_name":
                            model_name,

                        "requests":
                            count
                    }

                    for model_name,
                    count
                    in top_models
                ],

            "top_users":
                [

                    {
                        "user_id":
                            user_id,

                        "requests":
                            count
                    }

                    for user_id,
                    count
                    in top_users
                ]
        }


analytics_service = (
    AnalyticsService()
)