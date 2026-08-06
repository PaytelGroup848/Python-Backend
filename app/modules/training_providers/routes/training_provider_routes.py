from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.database import (
    get_db,
)

from app.modules.training_providers.services.training_provider_service import (
    training_provider_service,
)

from app.modules.training_providers.schemas.training_provider_create import (
    TrainingProviderCreate,
)

router = APIRouter(
    prefix="/training/providers",
    tags=["Training Providers"],
)


@router.get("")
async def list_training_providers(
    db: AsyncSession = Depends(get_db),
):
    providers = await training_provider_service.list_all(db=db)
    return providers


@router.get("/{provider_id}")
async def get_training_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
):
    provider = await training_provider_service.get_provider(
        db=db,
        provider_id=provider_id,
    )

    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"Training provider {provider_id} not found",
        )

    return provider


@router.post("")
async def create_training_provider(
    data: TrainingProviderCreate,
    db: AsyncSession = Depends(get_db),
):
    return await training_provider_service.create_provider(
        db=db,
        data=data,
    )
