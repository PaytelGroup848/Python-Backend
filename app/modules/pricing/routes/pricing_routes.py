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

from app.modules.pricing.schemas.pricing_schema import (
    PricingCreate
)

from app.modules.pricing.services.pricing_service import (
    pricing_service
)


router = APIRouter(

    prefix="/pricing",

    tags=["Pricing"]
)


@router.post("/")
async def create_pricing(

    payload: PricingCreate,

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        pricing_service.create_pricing(
            db,
            payload
        )
    )


@router.get("/")
async def get_pricing(

    db: AsyncSession = Depends(
        get_db
    )
):

    return await (
        pricing_service.get_all_pricing(
            db
        )
    )