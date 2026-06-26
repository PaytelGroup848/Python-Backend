from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.connector_registry.models.connector_instance import (
    ConnectorInstance
)


class ConnectorInstanceRepository:

    async def create(

        self,

        db: AsyncSession,

        connector_instance: ConnectorInstance

    ):

        db.add(
            connector_instance
        )

        await db.flush()

        await db.refresh(
            connector_instance
        )

        return connector_instance

    async def get_by_id(

        self,

        db: AsyncSession,

        connector_instance_id: int

    ):

        result = await db.execute(

            select(
                ConnectorInstance
            )
            .where(
                ConnectorInstance.id
                ==
                connector_instance_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_code(

        self,

        db: AsyncSession,

        instance_code: str

    ):

        result = await db.execute(

            select(
                ConnectorInstance
            )
            .where(
                ConnectorInstance.instance_code
                ==
                instance_code
            )
        )

        return result.scalar_one_or_none()

    async def list_by_implementation(

        self,

        db: AsyncSession,

        connector_implementation_id: int

    ):

        result = await db.execute(

            select(
                ConnectorInstance
            )
            .where(
                ConnectorInstance.connector_implementation_id
                ==
                connector_implementation_id
            )
        )

        return result.scalars().all()

    async def list_by_organization(

        self,

        db: AsyncSession,

        organization_id: int

    ):

        result = await db.execute(

            select(
                ConnectorInstance
            )
            .where(
                ConnectorInstance.organization_id
                ==
                organization_id
            )
        )

        return result.scalars().all()

    async def list_all(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                ConnectorInstance
            )
        )

        return result.scalars().all()

    async def update(

        self,

        db: AsyncSession,

        connector_instance: ConnectorInstance

    ):

        await db.flush()

        await db.refresh(
            connector_instance
        )

        return connector_instance


connector_instance_repository = (
    ConnectorInstanceRepository()
)