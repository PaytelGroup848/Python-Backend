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

from app.modules.billing.services.billing_service import (
    billing_service
)

router = APIRouter(

    prefix="/billing",

    tags=["Billing"]
)


@router.get(
    "/overview"
)
async def billing_overview(

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        billing_service
        .get_billing_overview(
            db
        )
    )