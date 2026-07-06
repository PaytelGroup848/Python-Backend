from abc import ABC, abstractmethod
from typing import Any

from app.modules.storage_runtime.contracts.storage_runtime import (
    StorageRuntime,
)


class StorageRuntimeFactory(ABC):

    @abstractmethod
    def create(
        self,
        configuration: dict[str, Any],
        provider_code: str,
        secret_reference: str | None = None,
    ) -> StorageRuntime:

        raise NotImplementedError