from sqlalchemy import func
from sqlalchemy import select

from app.models.api_request import (
    ApiRequest
)

from app.models.user import User

from app.models.api_key import ApiKey

from app.models.model import ModelRegistry


class AnalyticsRepository:

    async def total_requests(
        self,
        db
    ):

        result = await db.execute(

            select(
                func.count(
                    ApiRequest.id
                )
            )
        )

        return result.scalar()

    async def average_latency(
        self,
        db
    ):

        result = await db.execute(

            select(
                func.avg(
                    ApiRequest.latency_ms
                )
            )
        )

        return result.scalar()

    async def requests_by_provider(
        self,
        db
    ):

        result = await db.execute(

            select(

                ApiRequest.provider,

                func.count(
                    ApiRequest.id
                )

            ).group_by(
                ApiRequest.provider
            )
        )

        return result.all()
    
    async def total_users(
        self,
        db
    ):

        result = await db.execute(

            select(
                func.count(
                    User.id
                )
            )
        )

        return result.scalar()


    async def total_models(
        self,
        db
    ):

        result = await db.execute(

            select(
                func.count(
                    ModelRegistry.id
                )
            )
        )

        return result.scalar()


    async def total_api_keys(
        self,
        db
    ):

        result = await db.execute(

            select(
                func.count(
                    ApiKey.id
                )
            )
        )

        return result.scalar()


    async def top_models(
        self,
        db
    ):

        result = await db.execute(

            select(

                ApiRequest.model_name,

                func.count(
                    ApiRequest.id
                )

            )

            .group_by(
                ApiRequest.model_name
            )

            .order_by(
                func.count(
                    ApiRequest.id
                ).desc()
            )

            .limit(5)
        )

        return result.all()


    async def top_users(
        self,
        db
    ):

        result = await db.execute(

            select(

                ApiRequest.user_id,

                func.count(
                    ApiRequest.id
                )

            )

            .group_by(
                ApiRequest.user_id
            )

            .order_by(
                func.count(
                    ApiRequest.id
                ).desc()
            )

            .limit(5)
        )

        return result.all()


analytics_repository = (
    AnalyticsRepository()
)