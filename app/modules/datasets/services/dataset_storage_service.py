from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.storage_registry.repositories.storage_instance_repository import (
    storage_instance_repository,
)
from app.modules.storage_registry.models.storage_implementation import (
    StorageImplementation,
)
from app.modules.storage_registry.models.storage_instance import (
    StorageInstance,
)
from app.shared.constants.storage_scope_type import (
    StorageScopeType,
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
            # Auto-create local storage implementation and instance
            impl_res = await db.execute(
                select(StorageImplementation).where(
                    StorageImplementation.implementation_code == "LOCAL_FILESYSTEM"
                )
            )
            impl = impl_res.scalars().first()
            if not impl:
                impl = StorageImplementation(
                    implementation_code="LOCAL_FILESYSTEM",
                    implementation_version="1.0",
                    display_name="Local Filesystem Storage",
                    description="Default Local Storage",
                    runtime_type="LOCAL",
                    configuration_schema_json={},
                    capabilities_json={"read": True, "write": True, "delete": True},
                    is_active=True,
                )
                db.add(impl)
                await db.flush()

            instance = StorageInstance(
                storage_implementation_id=impl.id,
                scope_type=StorageScopeType.PLATFORM.value,
                instance_code=self.DEFAULT_PLATFORM_STORAGE_CODE,
                display_name="Platform Pipeline Dataset Storage",
                configuration_json={"root_directory": "/tmp/platform_storage"},
                is_active=True,
            )
            db.add(instance)
            await db.flush()

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