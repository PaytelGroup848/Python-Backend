from app.modules.storage_runtime.contracts.storage_runtime_factory import (
    StorageRuntimeFactory,
)


class StorageRuntimeFactoryRegistry:

    def __init__(
        self,
    ) -> None:

        self._factories: dict[
            str,
            StorageRuntimeFactory,
        ] = {}

    @staticmethod
    def _normalize(
        implementation_code: str,
    ) -> str:

        normalized = (
            implementation_code
            .strip()
            .upper()
        )

        if not normalized:

            raise ValueError(
                "Storage implementation code is required"
            )

        return normalized

    def register(
        self,
        implementation_code: str,
        factory: StorageRuntimeFactory,
    ) -> None:

        normalized = self._normalize(
            implementation_code
        )

        existing = self._factories.get(
            normalized
        )

        if existing is factory:

            return

        if existing is not None:

            raise ValueError(
                "Different storage runtime factory "
                "already registered: "
                f"{normalized}"
            )

        self._factories[
            normalized
        ] = factory

        print(
            "[REGISTER]",
            id(self),
            normalized,
            list(self._factories.keys()),
        )

    def get_factory(
        self,
        implementation_code: str,
    ) -> StorageRuntimeFactory:

        normalized = self._normalize(
            implementation_code
        )

        print(
            "[GET_FACTORY]",
            id(self),
            normalized,
            list(self._factories.keys()),
        )

        factory = self._factories.get(
            normalized
        )

        if factory is None:

            raise ValueError(
                "Storage runtime factory not registered: "
                f"{normalized}"
            )

        return factory


storage_runtime_factory_registry = (
    StorageRuntimeFactoryRegistry()
)