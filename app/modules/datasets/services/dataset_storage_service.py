from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.storage_registry.repositories.storage_instance_repository import (
    storage_instance_repository,
)

from app.modules.storage_runtime.schemas.resolved_storage_runtime import (
    ResolvedStorageRuntime,
)

from app.modules.storage_runtime.services.storage_resolution_service import (
    storage_resolution_service,
)

from app.shared.exceptions.business_exception import (
    BusinessException,
)


class DatasetStorageService:

    DEFAULT_PLATFORM_STORAGE_CODE = (
        "PLATFORM_PIPELINE_STORAGE"
    )

    async def resolve_platform_storage(
        self,
        db: AsyncSession,
    ) -> ResolvedStorageRuntime:

        instance = await (
            storage_instance_repository
            .get_active_platform_by_code(
                db=db,
                instance_code=(
                    self.DEFAULT_PLATFORM_STORAGE_CODE
                ),
            )
        )

        if instance is None:

            raise BusinessException(
                "Platform dataset storage "
                "is not configured."
            )

        return await (
            storage_resolution_service
            .resolve(
                db=db,
                storage_instance_id=instance.id,
            )
        )

    async def resolve_organization_storage(
        self,
        db: AsyncSession,
        organization_id: int,
        instance_code: str,
    ) -> ResolvedStorageRuntime:

        instance = await (
            storage_instance_repository
            .get_active_organization_by_code(
                db=db,
                organization_id=organization_id,
                instance_code=instance_code,
            )
        )

        if instance is None:

            raise BusinessException(
                "Organization dataset storage "
                "is not configured."
            )

        return await (
            storage_resolution_service
            .resolve(
                db=db,
                storage_instance_id=instance.id,
                organization_id=organization_id,
            )
        )

    async def resolve_workspace_storage(
        self,
        db: AsyncSession,
        organization_id: int,
        workspace_id: int,
        instance_code: str,
    ) -> ResolvedStorageRuntime:

        instance = await (
            storage_instance_repository
            .get_active_workspace_by_code(
                db=db,
                organization_id=organization_id,
                workspace_id=workspace_id,
                instance_code=instance_code,
            )
        )

        if instance is None:

            raise BusinessException(
                "Workspace dataset storage "
                "is not configured."
            )

        return await (
            storage_resolution_service
            .resolve(
                db=db,
                storage_instance_id=instance.id,
                organization_id=organization_id,
                workspace_id=workspace_id,
            )
        )


dataset_storage_service = (
    DatasetStorageService()
)