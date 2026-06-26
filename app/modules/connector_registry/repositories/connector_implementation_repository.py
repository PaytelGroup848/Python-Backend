from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.connector_registry.models.connector_implementation import (
    ConnectorImplementation
)


class ConnectorImplementationRepository:

    async def create(

        self,

        db: AsyncSession,

        connector_implementation: ConnectorImplementation

    ):

        db.add(
            connector_implementation
        )

        await db.flush()

        await db.refresh(
            connector_implementation
        )

        return connector_implementation

    async def get_by_id(

        self,

        db: AsyncSession,

        connector_implementation_id: int

    ):

        result = await db.execute(

            select(
                ConnectorImplementation
            )
            .where(
                ConnectorImplementation.id
                ==
                connector_implementation_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_code(

        self,

        db: AsyncSession,

        implementation_code: str

    ):

        result = await db.execute(

            select(
                ConnectorImplementation
            )
            .where(
                ConnectorImplementation.implementation_code
                ==
                implementation_code
            )
        )

        return result.scalar_one_or_none()
    
    async def get_by_code_and_version(

        self,

        db: AsyncSession,

        implementation_code: str,

        version: str

    ):

        result = await db.execute(

            select(
                ConnectorImplementation
            )
            .where(
                ConnectorImplementation.implementation_code
                == implementation_code,
                ConnectorImplementation.version
                == version
            )
        )

        return result.scalar_one_or_none()

    async def list_by_type(

        self,

        db: AsyncSession,

        connector_type_id: int

    ):

        result = await db.execute(

            select(
                ConnectorImplementation
            )
            .where(
                ConnectorImplementation.connector_type_id
                ==
                connector_type_id
            )
        )

        return result.scalars().all()

    async def list_all(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                ConnectorImplementation
            )
        )

        return result.scalars().all()

    async def update(

        self,

        db: AsyncSession,

        connector_implementation: ConnectorImplementation

    ):

        await db.flush()

        await db.refresh(
            connector_implementation
        )

        return connector_implementation


connector_implementation_repository = (
    ConnectorImplementationRepository()
)