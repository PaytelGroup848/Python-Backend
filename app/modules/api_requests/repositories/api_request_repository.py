from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.models.api_request import (
    ApiRequest
)


class ApiRequestRepository:

    async def create(
        self,
        db: AsyncSession,
        api_request: ApiRequest
    ):

        db.add(api_request)

        await db.commit()

        await db.refresh(
            api_request
        )

        return api_request

    async def get_user_requests(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(ApiRequest)

            .where(
                ApiRequest.user_id
                == user_id
            )

            .order_by(
                ApiRequest.created_at
                .desc()
            )
        )

        return (
            result.scalars()
            .all()
        )