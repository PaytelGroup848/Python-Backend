from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import get_db

from app.modules.connector_registry.schemas.connector_implementation_create import (
    ConnectorImplementationCreate
)

from app.modules.connector_registry.services.connector_implementation_service import (
    connector_implementation_service
)

router = APIRouter(
    prefix="/connector-implementations",
    tags=["Connector Implementations"]
)


@router.post("/")
async def create_connector_implementation(
    data: ConnectorImplementationCreate,
    db: AsyncSession = Depends(get_db)
):
    return await (
        connector_implementation_service
        .create_connector_implementation(
            db,
            data
        )
    )


@router.get("/{connector_implementation_id}")
async def get_connector_implementation(
    connector_implementation_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await (
        connector_implementation_service
        .get_connector_implementation(
            db,
            connector_implementation_id
        )
    )


@router.get("/")
async def list_connector_implementations(
    connector_type_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await (
        connector_implementation_service
        .list_connector_implementations(
            db,
            connector_type_id
        )
    )