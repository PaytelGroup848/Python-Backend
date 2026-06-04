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

from app.modules.analytics.services.analytics_service import (
    analytics_service
)

from app.modules.analytics.schemas.analytics_schema import (
    AnalyticsOverviewResponse
)


router = APIRouter(

    prefix="/analytics",

    tags=["Analytics"]
)


@router.get(

    "/overview",

    response_model=
    AnalyticsOverviewResponse
)
async def analytics_overview(

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        analytics_service
        .overview(db)
    )