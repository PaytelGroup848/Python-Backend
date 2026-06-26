from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import get_db

from app.modules.connector_registry.schemas.connector_instance_create import (
    ConnectorInstanceCreate
)

from app.modules.connector_registry.services.connector_instance_service import (
    connector_instance_service
)

router = APIRouter(
    prefix="/connector-instances",
    tags=["Connector Instances"]
)


@router.post("/")
async def create_connector_instance(
    data: ConnectorInstanceCreate,
    db: AsyncSession = Depends(get_db)
):
    return await (
        connector_instance_service
        .create_connector_instance(
            db,
            data
        )
    )


@router.get("/{connector_instance_id}")
async def get_connector_instance(
    connector_instance_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await (
        connector_instance_service
        .get_connector_instance(
            db,
            connector_instance_id
        )
    )


@router.get("/")
async def list_connector_instances(
    db: AsyncSession = Depends(get_db)
):
    return await (
        connector_instance_service
        .list_connector_instances(
            db
        )
    )