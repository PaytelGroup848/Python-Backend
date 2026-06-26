from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.connector_registry.models.connector_type import (
    ConnectorType
)


class ConnectorTypeRepository:

    async def create(

        self,

        db: AsyncSession,

        connector_type: ConnectorType

    ):

        db.add(
            connector_type
        )

        await db.flush()

        await db.refresh(
            connector_type
        )

        return connector_type

    async def get_by_id(

        self,

        db: AsyncSession,

        connector_type_id: int

    ):

        result = await db.execute(

            select(
                ConnectorType
            )
            .where(
                ConnectorType.id
                ==
                connector_type_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_code(

        self,

        db: AsyncSession,

        code: str

    ):

        result = await db.execute(

            select(
                ConnectorType
            )
            .where(
                ConnectorType.code
                ==
                code
            )
        )

        return result.scalar_one_or_none()

    async def list_all(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                ConnectorType
            )
        )

        return result.scalars().all()

    async def update(

        self,

        db: AsyncSession,

        connector_type: ConnectorType

    ):

        await db.flush()

        await db.refresh(
            connector_type
        )

        return connector_type


connector_type_repository = (
    ConnectorTypeRepository()
)