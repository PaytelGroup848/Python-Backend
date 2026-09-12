from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.modules.api_keys.services.api_key_service import api_key_service
from app.modules.api_keys.schemas.api_key_schema import (
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    ApiKeyListResponse,
    UserApiKeyUsageResponse,
)

router = APIRouter(
    prefix="/api-keys",
    tags=["API Keys"]
)


@router.post("", response_model=CreateApiKeyResponse)
async def create_api_key(
    payload: CreateApiKeyRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await api_key_service.create_api_key(
        db=db,
        user_id=current_user.id,
        name=payload.name
    )


@router.get("", response_model=ApiKeyListResponse)
async def get_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await api_key_service.get_user_keys(
        db=db,
        user_id=current_user.id
    )


@router.get("/usage", response_model=UserApiKeyUsageResponse)
async def get_api_key_usage(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await api_key_service.get_user_api_key_usage(
        db=db,
        user_id=current_user.id
    )


@router.patch("/{api_key_id}/disable")
async def disable_api_key(
    api_key_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        return await api_key_service.disable_api_key(
            db=db,
            user_id=current_user.id,
            api_key_id=api_key_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        return await api_key_service.delete_api_key(
            db=db,
            user_id=current_user.id,
            api_key_id=api_key_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
