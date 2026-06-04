from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.modules.api_requests.services.api_request_service import (
    api_request_service
)

from app.modules.api_requests.schemas.api_request_schema import (
    ApiRequestListResponse
)


router = APIRouter(

    prefix="/api-requests",

    tags=["API Requests"]
)


@router.get(
    "",
    response_model=
    ApiRequestListResponse
)
async def get_requests(

    db: AsyncSession = Depends(
        get_db
    )
):

    # temporary user

    user_id = 7

    return await (
        api_request_service
        .get_user_requests(
            db,
            user_id
        )
    )