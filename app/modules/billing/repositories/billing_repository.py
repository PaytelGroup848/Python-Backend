from sqlalchemy import (
    select,
    func
)

from app.models.api_request import (
    ApiRequest
)


class BillingRepository:

    async def get_global_usage(
        self,
        db
    ):

        result = await db.execute(

            select(

                func.count(
                    ApiRequest.id
                ),

                func.coalesce(
                    func.sum(
                        ApiRequest.total_tokens
                    ),
                    0
                )
            )
        )

        return result.first()

    async def get_provider_usage(
        self,
        db
    ):

        result = await db.execute(

            select(

                ApiRequest.provider,

                func.count(
                    ApiRequest.id
                ).label(
                    "requests"
                ),

                func.sum(
                    ApiRequest.total_tokens
                ).label(
                    "tokens"
                )
            )

            .group_by(
                ApiRequest.provider
            )
        )

        return result.fetchall()

    async def get_model_usage(
        self,
        db
    ):

        result = await db.execute(

            select(

                ApiRequest.model_name,

                func.count(
                    ApiRequest.id
                ).label(
                    "requests"
                ),

                func.sum(
                    ApiRequest.total_tokens
                ).label(
                    "tokens"
                )
            )

            .group_by(
                ApiRequest.model_name
            )
        )

        return result.fetchall()

    async def get_user_usage(
        self,
        db,
        user_id: int
    ):

        result = await db.execute(

            select(

                func.count(
                    ApiRequest.id
                ),

                func.coalesce(

                    func.sum(
                        ApiRequest.total_tokens
                    ),

                    0
                )
            )

            .where(
                ApiRequest.user_id
                == user_id
            )
        )

        return result.first()


billing_repository = (
    BillingRepository()
)