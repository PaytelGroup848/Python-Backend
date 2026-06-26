from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.connector_registry.models.connector_implementation import (
    ConnectorImplementation
)

from app.modules.connector_registry.schemas.connector_implementation_create import (
    ConnectorImplementationCreate
)

from app.modules.connector_registry.repositories.connector_implementation_repository import (
    connector_implementation_repository
)

from app.modules.connector_registry.repositories.connector_type_repository import (
    connector_type_repository
)


class ConnectorImplementationService:

    async def create_connector_implementation(

        self,

        db: AsyncSession,

        data: ConnectorImplementationCreate

    ):

        connector_type = await (

            connector_type_repository
            .get_by_id(
                db,
                data.connector_type_id
            )
        )

        if not connector_type:

            raise ValueError(
                "Connector type not found"
            )

        existing = await (

            connector_implementation_repository
            .get_by_code_and_version(
                db,
                data.implementation_code,
                data.version
            )
        )

        if existing:

            raise ValueError(
                "Connector implementation already exists"
            )

        connector_implementation = (

            ConnectorImplementation(
 
               **data.model_dump()
            )
        )

        return await (

            connector_implementation_repository
            .create(
                db,
                connector_implementation
            )
        )

    async def get_connector_implementation(

        self,

        db: AsyncSession,

        connector_implementation_id: int

    ):

        return await (

            connector_implementation_repository
            .get_by_id(
                db,
                connector_implementation_id
            )
        )

    async def list_connector_implementations(

        self,

        db: AsyncSession,

        connector_type_id: int

    ):

        return await (

            connector_implementation_repository
            .list_by_type(
                db,
                connector_type_id
            )
        )


connector_implementation_service = (
    ConnectorImplementationService()
)