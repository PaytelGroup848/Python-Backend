from abc import (
    ABC,
    abstractmethod,
)

from pathlib import Path
from typing import BinaryIO

from app.modules.pipeline_runtime.schemas.storage_object import (
    StorageObject,
)


class StorageRuntime(
    ABC
):

    @abstractmethod
    async def publish_file(
        self,
        source_path: Path,
        object_key: str,
        mime_type: str | None = None,
        metadata: dict | None = None,
    ) -> StorageObject:

        raise NotImplementedError

    @abstractmethod
    async def publish_bytes(
        self,
        content: bytes,
        object_key: str,
        mime_type: str | None = None,
        metadata: dict | None = None,
    ) -> StorageObject:

        raise NotImplementedError

    @abstractmethod
    async def open_read(
        self,
        storage_reference: str,
    ) -> BinaryIO:

        raise NotImplementedError

    @abstractmethod
    async def materialize(
        self,
        storage_reference: str,
        destination_path: Path,
    ) -> Path:

        raise NotImplementedError

    @abstractmethod
    async def exists(
        self,
        storage_reference: str,
    ) -> bool:

        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        storage_reference: str,
    ) -> None:

        raise NotImplementedError