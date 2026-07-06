from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.storage_registry.models.storage_instance import (
    StorageInstance,
)


class StorageInstanceRepository:

    async def create(
        self,
        db: AsyncSession,
        instance: StorageInstance,
    ) -> StorageInstance:

        db.add(instance)

        await db.flush()
        await db.refresh(instance)

        return instance

    async def get_by_id(
        self,
        db: AsyncSession,
        storage_instance_id: int,
    ) -> StorageInstance | None:

        result = await db.execute(
            select(StorageInstance)
            .where(
                StorageInstance.id
                ==
                storage_instance_id
            )
        )

        return result.scalar_one_or_none()

    async def get_active_by_id(
        self,
        db: AsyncSession,
        storage_instance_id: int,
    ) -> StorageInstance | None:

        result = await db.execute(
            select(StorageInstance)
            .where(
                StorageInstance.id
                ==
                storage_instance_id,

                StorageInstance.is_active.is_(
                    True
                ),
            )
        )

        return result.scalar_one_or_none()

    async def get_active_platform_by_code(
        self,
        db: AsyncSession,
        instance_code: str,
    ) -> StorageInstance | None:

        result = await db.execute(
            select(StorageInstance)
            .where(
                StorageInstance.scope_type
                ==
                "PLATFORM",

                StorageInstance.organization_id.is_(
                    None
                ),

                StorageInstance.workspace_id.is_(
                    None
                ),

                StorageInstance.instance_code
                ==
                instance_code,

                StorageInstance.is_active.is_(
                    True
                ),
            )
        )

        return result.scalar_one_or_none()

    async def get_active_organization_by_code(
        self,
        db: AsyncSession,
        organization_id: int,
        instance_code: str,
    ) -> StorageInstance | None:

        result = await db.execute(
            select(StorageInstance)
            .where(
                StorageInstance.scope_type
                ==
                "ORGANIZATION",

                StorageInstance.organization_id
                ==
                organization_id,

                StorageInstance.workspace_id.is_(
                    None
                ),

                StorageInstance.instance_code
                ==
                instance_code,

                StorageInstance.is_active.is_(
                    True
                ),
            )
        )

        return result.scalar_one_or_none()

    async def get_active_workspace_by_code(
        self,
        db: AsyncSession,
        organization_id: int,
        workspace_id: int,
        instance_code: str,
    ) -> StorageInstance | None:

        result = await db.execute(
            select(StorageInstance)
            .where(
                StorageInstance.scope_type
                ==
                "WORKSPACE",

                StorageInstance.organization_id
                ==
                organization_id,

                StorageInstance.workspace_id
                ==
                workspace_id,

                StorageInstance.instance_code
                ==
                instance_code,

                StorageInstance.is_active.is_(
                    True
                ),
            )
        )

        return result.scalar_one_or_none()

    async def get_by_scope_and_code(
        self,
        db: AsyncSession,
        scope_type: str,
        instance_code: str,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> StorageInstance | None:

        normalized_scope_type = (
            scope_type
            .strip()
            .upper()
        )

        statement = (
            select(StorageInstance)
            .where(
                StorageInstance.scope_type
                ==
                normalized_scope_type,

                StorageInstance.instance_code
                ==
                instance_code,
            )
        )

        if normalized_scope_type == "PLATFORM":

            statement = statement.where(
                StorageInstance.organization_id.is_(
                    None
                ),

                StorageInstance.workspace_id.is_(
                    None
                ),
            )

        elif normalized_scope_type == "ORGANIZATION":

            if organization_id is None:

                raise ValueError(
                    "organization_id is required "
                    "for ORGANIZATION storage scope"
                )

            statement = statement.where(
                StorageInstance.organization_id
                ==
                organization_id,

                StorageInstance.workspace_id.is_(
                    None
                ),
            )

        elif normalized_scope_type == "WORKSPACE":

            if organization_id is None:

                raise ValueError(
                    "organization_id is required "
                    "for WORKSPACE storage scope"
                )

            if workspace_id is None:

                raise ValueError(
                    "workspace_id is required "
                    "for WORKSPACE storage scope"
                )

            statement = statement.where(
                StorageInstance.organization_id
                ==
                organization_id,

                StorageInstance.workspace_id
                ==
                workspace_id,
            )

        else:

            raise ValueError(
                "Unsupported storage scope type: "
                f"{normalized_scope_type}"
            )

        result = await db.execute(
            statement
        )

        return result.scalar_one_or_none()


storage_instance_repository = (
    StorageInstanceRepository()
)