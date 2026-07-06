from app.modules.storage_runtime.factories.local_filesystem_storage_runtime_factory import (
    local_filesystem_storage_runtime_factory,
)

from app.modules.storage_runtime.registry.storage_runtime_factory_registry import (
    storage_runtime_factory_registry,
)


def register_storage_runtime_factories() -> None:

    storage_runtime_factory_registry.register(
        implementation_code="LOCAL_FILESYSTEM",
        factory=local_filesystem_storage_runtime_factory,
    )