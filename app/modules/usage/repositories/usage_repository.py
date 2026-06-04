from sqlalchemy import select
from sqlalchemy import func

from app.models.api_request import (
    ApiRequest
)


class UsageRepository:

    async def get_overview(
        self,
        db
    ):

        totals = await db.execute(

            select(

                func.coalesce(
                    func.sum(
                        ApiRequest.total_tokens
                    ),
                    0
                ),

                func.coalesce(
                    func.sum(
                        ApiRequest.prompt_tokens
                    ),
                    0
                ),

                func.coalesce(
                    func.sum(
                        ApiRequest.completion_tokens
                    ),
                    0
                )
            )
        )

        return totals.first()

    async def top_models(
        self,
        db
    ):

        result = await db.execute(

            select(

                ApiRequest.model_name,

                func.sum(
                    ApiRequest.total_tokens
                ).label(
                    "tokens"
                )

            )
            .group_by(
                ApiRequest.model_name
            )
            .order_by(
                func.sum(
                    ApiRequest.total_tokens
                ).desc()
            )
            .limit(10)
        )

        return result.all()

    async def top_users(
        self,
        db
    ):

        result = await db.execute(

            select(

                ApiRequest.user_id,

                func.sum(
                    ApiRequest.total_tokens
                ).label(
                    "tokens"
                )

            )
            .group_by(
                ApiRequest.user_id
            )
            .order_by(
                func.sum(
                    ApiRequest.total_tokens
                ).desc()
            )
            .limit(10)
        )

        return result.all()


usage_repository = (
    UsageRepository()
)