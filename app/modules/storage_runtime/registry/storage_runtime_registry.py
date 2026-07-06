from app.modules.storage_runtime.contracts.storage_runtime import (
    StorageRuntime,
)


class StorageRuntimeRegistry:

    def __init__(
        self,
    ):

        self._runtimes: dict[
            str,
            StorageRuntime,
        ] = {}

    def register(
        self,
        runtime_type: str,
        runtime: StorageRuntime,
    ) -> None:

        normalized_runtime_type = (
            runtime_type
            .strip()
            .upper()
        )

        if not normalized_runtime_type:

            raise ValueError(
                "Storage runtime type is required"
            )

        if (
            normalized_runtime_type
            in
            self._runtimes
        ):

            raise ValueError(
                "Storage runtime already registered: "
                f"{normalized_runtime_type}"
            )

        self._runtimes[
            normalized_runtime_type
        ] = runtime

    def get_runtime(
        self,
        runtime_type: str,
    ) -> StorageRuntime:

        normalized_runtime_type = (
            runtime_type
            .strip()
            .upper()
        )

        runtime = self._runtimes.get(
            normalized_runtime_type
        )

        if runtime is None:

            raise ValueError(
                "Storage runtime not registered: "
                f"{normalized_runtime_type}"
            )

        return runtime


storage_runtime_registry = (
    StorageRuntimeRegistry()
)