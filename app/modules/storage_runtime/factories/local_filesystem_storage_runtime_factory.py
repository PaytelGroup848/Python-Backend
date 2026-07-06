from pathlib import Path
from typing import Any

from app.modules.storage_runtime.contracts.storage_runtime import (
    StorageRuntime,
)

from app.modules.storage_runtime.contracts.storage_runtime_factory import (
    StorageRuntimeFactory,
)

from app.modules.storage_runtime.runtimes.local_filesystem_storage_runtime import (
    LocalFilesystemStorageRuntime,
)

from app.modules.storage_runtime.schemas.local_filesystem_storage_configuration import (
    LocalFilesystemStorageConfiguration,
)


class LocalFilesystemStorageRuntimeFactory(
    StorageRuntimeFactory
):

    def create(
        self,
        configuration: dict[str, Any],
        provider_code: str,
        secret_reference: str | None = None,
    ) -> StorageRuntime:

        validated = (
            LocalFilesystemStorageConfiguration
            .model_validate(
                configuration
            )
        )

        return LocalFilesystemStorageRuntime(
            root_directory=Path(
                validated.root_directory
            ),
            provider_code=provider_code,
        )


local_filesystem_storage_runtime_factory = (
    LocalFilesystemStorageRuntimeFactory()
)