from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.storage_registry.repositories.storage_instance_repository import (
    storage_instance_repository,
)

from app.modules.storage_registry.repositories.storage_implementation_repository import (
    storage_implementation_repository,
)

from app.modules.storage_runtime.contracts.storage_runtime import (
    StorageRuntime,
)

from app.modules.storage_runtime.registry.storage_runtime_registry import (
    storage_runtime_registry,
)


class StorageRuntimeResolverService:

    async def resolve_by_instance_id(
        self,
        db: AsyncSession,
        storage_instance_id: int,
    ) -> StorageRuntime:

        instance = await (
            storage_instance_repository
            .get_active_by_id(
                db=db,
                storage_instance_id=storage_instance_id,
            )
        )

        if instance is None:

            raise ValueError(
                "Active storage instance not found: "
                f"{storage_instance_id}"
            )

        implementation = await (
            storage_implementation_repository
            .get_by_id(
                db=db,
                implementation_id=(
                    instance.storage_implementation_id
                ),
            )
        )

        if implementation is None:

            raise ValueError(
                "Storage implementation not found: "
                f"{instance.storage_implementation_id}"
            )

        if not implementation.is_active:

            raise ValueError(
                "Storage implementation is inactive: "
                f"{implementation.id}"
            )

        return (
            storage_runtime_registry
            .get_runtime(
                implementation.runtime_type
            )
        )


storage_runtime_resolver_service = (
    StorageRuntimeResolverService()
)