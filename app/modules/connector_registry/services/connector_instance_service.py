from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.connector_registry.models.connector_instance import (
    ConnectorInstance
)

from app.modules.connector_registry.schemas.connector_instance_create import (
    ConnectorInstanceCreate
)

from app.modules.connector_registry.repositories.connector_instance_repository import (
    connector_instance_repository
)

from app.modules.connector_registry.repositories.connector_implementation_repository import (
    connector_implementation_repository
)


class ConnectorInstanceService:

    async def create_connector_instance(

        self,

        db: AsyncSession,

        data: ConnectorInstanceCreate

    ):

        implementation = await (

            connector_implementation_repository
            .get_by_id(
                db,
                data.connector_implementation_id
            )
        )

        if not implementation:

            raise ValueError(
                "Connector implementation not found"
            )

        existing = await (

            connector_instance_repository
            .get_by_code(
                db,
                data.instance_code
            )
        )

        if existing:

            raise ValueError(
                "Connector instance already exists"
            )

        connector_instance = ConnectorInstance(

            **data.model_dump()

        )

        return await (

            connector_instance_repository
            .create(
                db,
                connector_instance
            )
        )

    async def get_connector_instance(

        self,

        db: AsyncSession,

        connector_instance_id: int

    ):

        return await (

            connector_instance_repository
            .get_by_id(
                db,
                connector_instance_id
            )
        )

    async def list_connector_instances(

        self,

        db: AsyncSession

    ):

        return await (

            connector_instance_repository
            .list_all(
                db
            )
        )

    async def list_by_organization(

        self,

        db: AsyncSession,

        organization_id: int

    ):

        return await (

            connector_instance_repository
            .list_by_organization(
                db,
                organization_id
            )
        )


connector_instance_service = (
    ConnectorInstanceService()
)