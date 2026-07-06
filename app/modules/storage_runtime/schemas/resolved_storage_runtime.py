from dataclasses import dataclass

from app.modules.storage_runtime.contracts.storage_runtime import (
    StorageRuntime,
)


@dataclass(slots=True)
class ResolvedStorageRuntime:

    storage_instance_id: int

    storage_implementation_id: int

    instance_code: str

    implementation_code: str

    implementation_version: str

    runtime: StorageRuntime