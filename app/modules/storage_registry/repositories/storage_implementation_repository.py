from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.storage_registry.models.storage_implementation import (
    StorageImplementation,
)


class StorageImplementationRepository:

    async def create(
        self,
        db: AsyncSession,
        implementation: StorageImplementation,
    ) -> StorageImplementation:

        db.add(implementation)

        await db.flush()
        await db.refresh(implementation)

        return implementation

    async def get_by_id(
        self,
        db: AsyncSession,
        implementation_id: int,
    ) -> StorageImplementation | None:

        result = await db.execute(
            select(StorageImplementation)
            .where(
                StorageImplementation.id
                ==
                implementation_id
            )
        )

        return result.scalar_one_or_none()

    async def get_active_by_code(
        self,
        db: AsyncSession,
        implementation_code: str,
        implementation_version: str | None = None,
    ) -> StorageImplementation | None:

        statement = (
            select(StorageImplementation)
            .where(
                StorageImplementation.implementation_code
                ==
                implementation_code,
                StorageImplementation.is_active
                ==
                True,
            )
        )

        if implementation_version is not None:
            statement = statement.where(
                StorageImplementation.implementation_version
                ==
                implementation_version
            )

        statement = statement.order_by(
            StorageImplementation.id.desc()
        )

        result = await db.execute(statement)

        return result.scalars().first()
    
    async def get_by_code_and_version(
        self,
        db: AsyncSession,
        implementation_code: str,
        implementation_version: str,
    ) -> StorageImplementation | None:

        result = await db.execute(
            select(StorageImplementation)
            .where(
                StorageImplementation.implementation_code
                ==
                implementation_code,

                StorageImplementation.implementation_version
                ==
                implementation_version,
            )
        )

        return result.scalar_one_or_none()


storage_implementation_repository = (
    StorageImplementationRepository()
)