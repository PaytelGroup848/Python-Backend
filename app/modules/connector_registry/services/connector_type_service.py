from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.connector_registry.models.connector_type import (
    ConnectorType
)

from app.modules.connector_registry.schemas.connector_type_create import (
    ConnectorTypeCreate
)

from app.modules.connector_registry.repositories.connector_type_repository import (
    connector_type_repository
)


class ConnectorTypeService:

    async def create_connector_type(

        self,

        db: AsyncSession,

        data: ConnectorTypeCreate

    ):

        existing = await (
            connector_type_repository
            .get_by_code(
                db,
                data.code
            )
        )

        if existing:

            raise ValueError(
                "Connector type already exists"
            )

        connector_type = ConnectorType(

            **data.model_dump()

        )

        return await (
            connector_type_repository
            .create(
                db,
                connector_type
            )
        )

    async def get_connector_type(

        self,

        db: AsyncSession,

        connector_type_id: int

    ):

        return await (
            connector_type_repository
            .get_by_id(
                db,
                connector_type_id
            )
        )

    async def list_connector_types(

        self,

        db: AsyncSession

    ):

        return await (
            connector_type_repository
            .list_all(
                db
            )
        )


connector_type_service = (
    ConnectorTypeService()
)