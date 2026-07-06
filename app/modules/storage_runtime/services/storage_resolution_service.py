from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.storage_registry.models.storage_instance import (
    StorageInstance,
)

from app.modules.storage_registry.repositories.storage_instance_repository import (
    storage_instance_repository,
)

from app.modules.storage_registry.repositories.storage_implementation_repository import (
    storage_implementation_repository,
)

from app.modules.storage_runtime.registry.storage_runtime_factory_registry import (
    storage_runtime_factory_registry,
)

from app.modules.storage_runtime.schemas.resolved_storage_runtime import (
    ResolvedStorageRuntime,
)


class StorageResolutionService:

    @staticmethod
    def _authorize_scope(
        instance: StorageInstance,
        organization_id: int | None,
        workspace_id: int | None,
    ) -> None:

        scope_type = (
            instance.scope_type
            .strip()
            .upper()
        )

        if scope_type == "PLATFORM":

            if (
                instance.organization_id is not None
                or
                instance.workspace_id is not None
            ):

                raise ValueError(
                    "Invalid PLATFORM storage "
                    "instance scope identity"
                )

            return

        if scope_type == "ORGANIZATION":

            if instance.organization_id is None:

                raise ValueError(
                    "Invalid ORGANIZATION storage "
                    "instance scope identity"
                )

            if instance.workspace_id is not None:

                raise ValueError(
                    "Invalid ORGANIZATION storage "
                    "instance scope identity"
                )

            if organization_id is None:

                raise PermissionError(
                    "Organization context is required "
                    "for ORGANIZATION storage scope"
                )

            if (
                instance.organization_id
                !=
                organization_id
            ):

                raise PermissionError(
                    "Storage instance does not belong "
                    "to the requested organization"
                )

            return

        if scope_type == "WORKSPACE":

            if instance.organization_id is None:

                raise ValueError(
                    "Invalid WORKSPACE storage "
                    "instance scope identity"
                )

            if instance.workspace_id is None:

                raise ValueError(
                    "Invalid WORKSPACE storage "
                    "instance scope identity"
                )

            if organization_id is None:

                raise PermissionError(
                    "Organization context is required "
                    "for WORKSPACE storage scope"
                )

            if workspace_id is None:

                raise PermissionError(
                    "Workspace context is required "
                    "for WORKSPACE storage scope"
                )

            if (
                instance.organization_id
                !=
                organization_id
            ):

                raise PermissionError(
                    "Storage instance does not belong "
                    "to the requested organization"
                )

            if (
                instance.workspace_id
                !=
                workspace_id
            ):

                raise PermissionError(
                    "Storage instance does not belong "
                    "to the requested workspace"
                )

            return

        raise ValueError(
            "Unsupported storage scope type: "
            f"{scope_type}"
        )

    async def resolve(
        self,
        db: AsyncSession,
        storage_instance_id: int,
        organization_id: int | None = None,
        workspace_id: int | None = None,
    ) -> ResolvedStorageRuntime:

        instance = await (
            storage_instance_repository
            .get_active_by_id(
                db=db,
                storage_instance_id=(
                    storage_instance_id
                ),
            )
        )

        if instance is None:

            raise ValueError(
                "Active storage instance not found: "
                f"{storage_instance_id}"
            )

        self._authorize_scope(
            instance=instance,
            organization_id=organization_id,
            workspace_id=workspace_id,
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

        factory = (
            storage_runtime_factory_registry
            .get_factory(
                implementation_code=(
                    implementation.implementation_code
                )
            )
        )

        runtime = factory.create(
            configuration=(
                instance.configuration_json
                or
                {}
            ),
            provider_code=(
                instance.instance_code
            ),
            secret_reference=(
                instance.secret_reference
            ),
        )

        return ResolvedStorageRuntime(
            storage_instance_id=instance.id,
            storage_implementation_id=(
                implementation.id
            ),
            instance_code=instance.instance_code,
            implementation_code=(
                implementation.implementation_code
            ),
            implementation_version=(
                implementation.implementation_version
            ),
            runtime=runtime,
        )


storage_resolution_service = (
    StorageResolutionService()
)