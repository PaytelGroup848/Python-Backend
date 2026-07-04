from pathlib import Path

from app.modules.connector_runtime.contracts.base_connector_runtime import (
    BaseConnectorRuntime
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class LocalFilesystemRuntime(
    BaseConnectorRuntime
):

    async def execute(
        self,
        configuration: dict
    ) -> dict:

        root_path_value = (
            configuration.get(
                "root_path"
            )
        )

        if not root_path_value:

            raise BusinessException(
                "root_path is required."
            )

        root_path = Path(
            root_path_value
        )

        if not root_path.exists():

            raise BusinessException(
                f"Root path '{root_path}' does not exist."
            )

        if not root_path.is_dir():

            raise BusinessException(
                f"Root path '{root_path}' is not a directory."
            )

        recursive = configuration.get(
            "recursive",
            True
        )

        allowed_extensions = configuration.get(
            "allowed_extensions",
            []
        )

        normalized_extensions = {
            str(extension).lower()
            for extension in allowed_extensions
        }

        iterator = (
            root_path.rglob("*")
            if recursive
            else root_path.glob("*")
        )

        files = []

        for path in iterator:

            if not path.is_file():
                continue

            if (
                normalized_extensions
                and
                path.suffix.lower()
                not in normalized_extensions
            ):
                continue

            files.append(
                {
                    "path": str(path),
                    "name": path.name,
                    "extension": path.suffix.lower(),
                    "size_bytes": path.stat().st_size
                }
            )

        return {
            "status": "SUCCESS",
            "root_path": str(root_path),
            "recursive": recursive,
            "files_discovered": len(files),
            "files": files
        }


local_filesystem_runtime = (
    LocalFilesystemRuntime()
)