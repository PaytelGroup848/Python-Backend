from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from app.modules.storage_registry.models.storage_implementation import (
    StorageImplementation,
)

from app.modules.storage_registry.models.storage_instance import (
    StorageInstance,
)

from app.modules.storage_registry.repositories.storage_implementation_repository import (
    storage_implementation_repository,
)

from app.modules.storage_registry.repositories.storage_instance_repository import (
    storage_instance_repository,
)

from app.shared.constants.storage_scope_type import (
    StorageScopeType,
)


class StorageProvisioningService:

    async def provision_local_filesystem_platform_storage(
        self,
        db: AsyncSession,
    ) -> StorageInstance:

        implementation_code = (
            "LOCAL_FILESYSTEM"
        )

        implementation_version = (
            "1"
        )

        instance_code = (
            "PLATFORM_PIPELINE_STORAGE"
        )

        implementation = await (
            storage_implementation_repository
            .get_by_code_and_version(
                db=db,
                implementation_code=(
                    implementation_code
                ),
                implementation_version=(
                    implementation_version
                ),
            )
        )

        if implementation is None:

            implementation = StorageImplementation(
                implementation_code=(
                    implementation_code
                ),
                implementation_version=(
                    implementation_version
                ),
                display_name=(
                    "Local Filesystem Storage"
                ),
                description=(
                    "Local filesystem storage runtime"
                ),
                runtime_type=(
                    "LOCAL_FILESYSTEM"
                ),
                configuration_schema_json={
                    "type": "object",
                    "required": [
                        "root_directory",
                    ],
                    "properties": {
                        "root_directory": {
                            "type": "string",
                            "minLength": 1,
                        },
                    },
                    "additionalProperties": False,
                },
                capabilities_json={
                    "publish_file": True,
                    "publish_bytes": True,
                    "open_read": True,
                    "materialize": True,
                    "exists": True,
                    "delete": True,
                },
                is_active=True,
            )

            implementation = await (
                storage_implementation_repository
                .create(
                    db=db,
                    implementation=implementation,
                )
            )

        else:

            implementation.display_name = (
                "Local Filesystem Storage"
            )

            implementation.description = (
                "Local filesystem storage runtime"
            )

            implementation.runtime_type = (
                "LOCAL_FILESYSTEM"
            )

            implementation.configuration_schema_json = {
                "type": "object",
                "required": [
                    "root_directory",
                ],
                "properties": {
                    "root_directory": {
                        "type": "string",
                        "minLength": 1,
                    },
                },
                "additionalProperties": False,
            }

            implementation.capabilities_json = {
                "publish_file": True,
                "publish_bytes": True,
                "open_read": True,
                "materialize": True,
                "exists": True,
                "delete": True,
            }

            implementation.is_active = True

            await db.flush()

        instance = await (
            storage_instance_repository
            .get_by_scope_and_code(
                db=db,
                scope_type=(
                    StorageScopeType.PLATFORM.value
                ),
                instance_code=instance_code,
            )
        )

        desired_configuration = {
            "root_directory": (
                settings.PIPELINE_STORAGE_LOCAL_ROOT
            ),
        }

        if instance is None:

            instance = StorageInstance(
                storage_implementation_id=(
                    implementation.id
                ),
                scope_type=(
                    StorageScopeType.PLATFORM.value
                ),
                organization_id=None,
                workspace_id=None,
                instance_code=instance_code,
                display_name=(
                    "Platform Pipeline Storage"
                ),
                configuration_json=(
                    desired_configuration
                ),
                secret_reference=None,
                is_active=True,
            )

            instance = await (
                storage_instance_repository
                .create(
                    db=db,
                    instance=instance,
                )
            )

        else:

            instance.storage_implementation_id = (
                implementation.id
            )

            instance.scope_type = (
                StorageScopeType.PLATFORM.value
            )

            instance.organization_id = None

            instance.workspace_id = None

            instance.display_name = (
                "Platform Pipeline Storage"
            )

            instance.configuration_json = (
                desired_configuration
            )

            instance.secret_reference = None

            instance.is_active = True

            await db.flush()
            await db.refresh(instance)

        return instance


storage_provisioning_service = (
    StorageProvisioningService()
)