from app.modules.connector_runtime.contracts.base_connector_runtime import (
    BaseConnectorRuntime
)

from app.modules.connector_runtime.runtimes.local_filesystem_runtime import (
    local_filesystem_runtime
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class ConnectorRuntimeRegistry:

    def __init__(
        self
    ):

        self._runtimes: dict[
            str,
            BaseConnectorRuntime
        ] = {}

        self.register(
            implementation_code="local_filesystem_v1",
            runtime=local_filesystem_runtime
        )

    def register(
        self,
        implementation_code: str,
        runtime: BaseConnectorRuntime
    ) -> None:

        if not implementation_code:

            raise ValueError(
                "implementation_code is required."
            )

        self._runtimes[
            implementation_code
        ] = runtime

    def get_runtime(
        self,
        implementation_code: str
    ) -> BaseConnectorRuntime:

        runtime = self._runtimes.get(
            implementation_code
        )

        if runtime is None:

            raise BusinessException(
                "No connector runtime registered for "
                f"'{implementation_code}'."
            )

        return runtime


connector_runtime_registry = (
    ConnectorRuntimeRegistry()
)