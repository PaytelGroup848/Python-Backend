import asyncio
import hashlib
import shutil

from pathlib import Path
from typing import BinaryIO

from app.modules.pipeline_runtime.schemas.storage_object import (
    StorageObject,
)

from app.modules.storage_runtime.contracts.storage_runtime import (
    StorageRuntime,
)


class LocalFilesystemStorageRuntime(
    StorageRuntime
):

    def __init__(
        self,
        root_directory: Path,
        provider_code: str,
    ):

        self._root_directory = (
            root_directory.resolve()
        )

        self._provider_code = (
            provider_code
            .strip()
            .upper()
        )

    def _resolve_object_path(
        self,
        object_key: str,
    ) -> Path:

        normalized_key = (
            object_key
            .replace("\\", "/")
            .lstrip("/")
        )

        if not normalized_key:

            raise ValueError(
                "Storage object key is required"
            )

        candidate = (
            self._root_directory
            /
            normalized_key
        ).resolve()

        try:

            candidate.relative_to(
                self._root_directory
            )

        except ValueError as exc:

            raise ValueError(
                "Storage object key escapes root directory"
            ) from exc

        return candidate

    @staticmethod
    def _calculate_checksum(
        path: Path,
    ) -> str:

        digest = hashlib.sha256()

        with path.open("rb") as stream:

            for block in iter(
                lambda: stream.read(
                    1024 * 1024
                ),
                b"",
            ):

                digest.update(block)

        return digest.hexdigest()

    async def publish_file(
        self,
        source_path: Path,
        object_key: str,
        mime_type: str | None = None,
        metadata: dict | None = None,
    ) -> StorageObject:

        source = source_path.resolve()

        if not source.exists():

            raise FileNotFoundError(
                str(source)
            )

        if not source.is_file():

            raise ValueError(
                "Storage source must be a file"
            )

        destination = (
            self._resolve_object_path(
                object_key
            )
        )

        await asyncio.to_thread(
            destination.parent.mkdir,
            parents=True,
            exist_ok=True,
        )

        await asyncio.to_thread(
            shutil.copy2,
            source,
            destination,
        )

        checksum = await asyncio.to_thread(
            self._calculate_checksum,
            destination,
        )

        size_bytes = (
            await asyncio.to_thread(
                lambda: destination.stat().st_size
            )
        )

        return StorageObject(
            storage_provider=(
                self._provider_code
            ),
            storage_reference=(
                object_key
                .replace("\\", "/")
                .lstrip("/")
            ),
            mime_type=mime_type,
            size_bytes=size_bytes,
            checksum=checksum,
            metadata=metadata or {},
        )

    async def publish_bytes(
        self,
        content: bytes,
        object_key: str,
        mime_type: str | None = None,
        metadata: dict | None = None,
    ) -> StorageObject:

        destination = (
            self._resolve_object_path(
                object_key
            )
        )

        await asyncio.to_thread(
            destination.parent.mkdir,
            parents=True,
            exist_ok=True,
        )

        await asyncio.to_thread(
            destination.write_bytes,
            content,
        )

        checksum = (
            hashlib.sha256(
                content
            )
            .hexdigest()
        )

        return StorageObject(
            storage_provider=(
                self._provider_code
            ),
            storage_reference=(
                object_key
                .replace("\\", "/")
                .lstrip("/")
            ),
            mime_type=mime_type,
            size_bytes=len(content),
            checksum=checksum,
            metadata=metadata or {},
        )

    async def open_read(
        self,
        storage_reference: str,
    ) -> BinaryIO:

        path = self._resolve_object_path(
            storage_reference
        )

        if not path.exists():

            raise FileNotFoundError(
                storage_reference
            )

        if not path.is_file():

            raise ValueError(
                "Storage reference is not a file"
            )

        return path.open("rb")

    async def materialize(
        self,
        storage_reference: str,
        destination_path: Path,
    ) -> Path:

        source = self._resolve_object_path(
            storage_reference
        )

        if not source.exists():

            raise FileNotFoundError(
                storage_reference
            )

        destination = (
            destination_path.resolve()
        )

        await asyncio.to_thread(
            destination.parent.mkdir,
            parents=True,
            exist_ok=True,
        )

        await asyncio.to_thread(
            shutil.copy2,
            source,
            destination,
        )

        return destination

    async def exists(
        self,
        storage_reference: str,
    ) -> bool:

        path = self._resolve_object_path(
            storage_reference
        )

        return await asyncio.to_thread(
            path.is_file
        )

    async def delete(
        self,
        storage_reference: str,
    ) -> None:

        path = self._resolve_object_path(
            storage_reference
        )

        if await asyncio.to_thread(
            path.exists
        ):

            await asyncio.to_thread(
                path.unlink
            )