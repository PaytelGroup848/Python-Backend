from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

from app.modules.api_keys.services.api_key_service import (
    api_key_service
)

from app.modules.api_keys.schemas.api_key_schema import (
    CreateApiKeyRequest
)


router = APIRouter(
    prefix="/api-keys",
    tags=["API Keys"]
)


@router.post("")
async def create_api_key(
    payload: CreateApiKeyRequest,
    db: AsyncSession = Depends(get_db)
):

    # temporary hardcoded user
    user_id = 7

    return await (
        api_key_service.create_api_key(
            db=db,
            user_id=user_id,
            name=payload.name
        )
    )


@router.get("")
async def get_api_keys(
    db: AsyncSession = Depends(get_db)
):

    # temporary hardcoded user
    user_id = 7

    return await (
        api_key_service.get_user_keys(
            db=db,
            user_id=user_id
        )
    )

@router.patch(
    "/{api_key_id}/disable"
)
async def disable_api_key(
    api_key_id: int,
    db: AsyncSession = Depends(get_db)
):

    return await (
        api_key_service
        .disable_api_key(
            db=db,
            api_key_id=api_key_id
        )
    )

@router.patch(
    "/{api_key_id}/enable"
)
async def enable_api_key(
    api_key_id: int,
    db: AsyncSession = Depends(get_db)
):

    return await (
        api_key_service
        .enable_api_key(
            db=db,
            api_key_id=api_key_id
        )
    )