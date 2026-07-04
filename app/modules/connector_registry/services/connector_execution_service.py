from copy import deepcopy

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.connector_registry.repositories.connector_instance_repository import (
    connector_instance_repository
)

from app.modules.connector_registry.repositories.connector_implementation_repository import (
    connector_implementation_repository
)

from app.modules.connector_runtime.registry.connector_runtime_registry import (
    connector_runtime_registry
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class ConnectorExecutionService:

    async def execute(
        self,
        db: AsyncSession,
        connector_instance_id: int,
        configuration: dict | None = None
    ) -> dict:

        #
        # STEP 1:
        # Resolve connector instance from database
        #
        connector_instance = await (
            connector_instance_repository
            .get_by_id(
                db,
                connector_instance_id
            )
        )

        if not connector_instance:

            raise BusinessException(
                "Connector instance not found."
            )

        #
        # STEP 2:
        # Ensure connector instance is active
        #
        if (
            str(connector_instance.status).upper()
            !=
            "ACTIVE"
        ):

            raise BusinessException(
                "Connector instance is not active."
            )

        #
        # STEP 3:
        # Resolve connector implementation from database
        #
        connector_implementation = await (
            connector_implementation_repository
            .get_by_id(
                db,
                connector_instance.connector_implementation_id
            )
        )

        if not connector_implementation:

            raise BusinessException(
                "Connector implementation not found."
            )

        #
        # STEP 4:
        # Ensure connector implementation is active
        #
        if (
            str(connector_implementation.status).upper()
            !=
            "ACTIVE"
        ):

            raise BusinessException(
                "Connector implementation is not active."
            )

        #
        # STEP 5:
        # Read implementation code from DB configuration
        #
        implementation_code = (
            connector_implementation
            .implementation_code
        )

        if not implementation_code:

            raise BusinessException(
                "Connector implementation code is missing."
            )

        #
        # STEP 6:
        # Resolve executable runtime from runtime registry
        #
        runtime = (
            connector_runtime_registry
            .get_runtime(
                implementation_code
            )
        )

        #
        # STEP 7:
        # Copy persistent connector instance configuration
        #
        # We intentionally avoid mutating the SQLAlchemy
        # JSONB-backed configuration object.
        #
        instance_configuration = deepcopy(
            connector_instance.configuration_json
            or
            {}
        )

        #
        # STEP 8:
        # Merge optional execution-time configuration
        #
        # Persistent DB configuration is the base.
        # Execution-time configuration may override it
        # for the current execution only.
        #
        execution_configuration = {
            **instance_configuration,
            **(
                configuration
                or
                {}
            )
        }

        #
        # STEP 9:
        # Execute the resolved connector runtime
        #
        runtime_result = await (
            runtime.execute(
                configuration=execution_configuration
            )
        )

        #
        # STEP 10:
        # Validate runtime contract
        #
        if not isinstance(
            runtime_result,
            dict
        ):

            raise BusinessException(
                "Connector runtime returned an invalid result."
            )

        #
        # STEP 11:
        # Return generic execution envelope
        #
        return {
            "connector_instance_id": (
                connector_instance.id
            ),
            "connector_implementation_id": (
                connector_implementation.id
            ),
            "implementation_code": (
                implementation_code
            ),
            "runtime_result": (
                runtime_result
            )
        }


connector_execution_service = (
    ConnectorExecutionService()
)