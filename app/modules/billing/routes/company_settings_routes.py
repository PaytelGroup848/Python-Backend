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

from app.core.security import (
    require_role
)

from app.modules.billing.services.company_settings_service import (
    company_settings_service
)

router = APIRouter(

    prefix="/admin/company-settings",

    tags=["Company Settings"]
)


@router.get("")
async def get_company_settings(

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    settings = await (
        company_settings_service
        .get_company_settings(
            db
        )
    )

    return settings


@router.put("")
async def update_company_settings(

    payload: dict,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    settings = await (
        company_settings_service
        .update_company_settings(
            db,
            payload
        )
    )

    return settings