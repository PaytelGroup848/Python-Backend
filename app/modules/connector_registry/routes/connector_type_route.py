from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import get_db

from app.modules.connector_registry.schemas.connector_type_create import (
    ConnectorTypeCreate
)

from app.modules.connector_registry.services.connector_type_service import (
    connector_type_service
)

router = APIRouter(
    prefix="/connector-types",
    tags=["Connector Types"]
)


@router.post("/")
async def create_connector_type(
    data: ConnectorTypeCreate,
    db: AsyncSession = Depends(get_db)
):
    return await (
        connector_type_service
        .create_connector_type(
            db,
            data
        )
    )


@router.get("/{connector_type_id}")
async def get_connector_type(
    connector_type_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await (
        connector_type_service
        .get_connector_type(
            db,
            connector_type_id
        )
    )


@router.get("/")
async def list_connector_types(
    db: AsyncSession = Depends(get_db)
):
    return await (
        connector_type_service
        .list_connector_types(
            db
        )
    )