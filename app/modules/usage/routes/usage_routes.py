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

from app.modules.usage.services.usage_service import (
    usage_service
)


router = APIRouter(

    prefix="/usage",

    tags=["Usage"]
)


@router.get(
    "/overview"
)
async def usage_overview(

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        usage_service
        .get_usage_overview(
            db
        )
    )