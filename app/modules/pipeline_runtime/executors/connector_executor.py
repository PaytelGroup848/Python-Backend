from copy import deepcopy
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.pipeline_runtime.executors.base_executor import (
    BaseExecutor,
)

from app.modules.pipeline_runtime.schemas.executor_result import (
    ExecutorResult,
)

from app.modules.pipeline_runtime.schemas.pipeline_execution_context import (
    PipelineExecutionContext,
)

from app.modules.connector_registry.services.connector_execution_service import (
    connector_execution_service,
)


class ConnectorExecutor(
    BaseExecutor,
):

    @staticmethod
    def _normalize_outputs(
        runtime_result: Any,
    ) -> list[dict[str, Any]]:

        if runtime_result is None:
            return []

        if isinstance(
            runtime_result,
            list,
        ):

            outputs: list[
                dict[str, Any]
            ] = []

            for item in runtime_result:

                if not isinstance(
                    item,
                    dict,
                ):
                    raise ValueError(
                        "Connector runtime output list "
                        "must contain dictionaries."
                    )

                outputs.append(
                    deepcopy(item)
                )

            return outputs

        if isinstance(
            runtime_result,
            dict,
        ):

            files = runtime_result.get(
                "files"
            )

            if files is not None:

                if not isinstance(
                    files,
                    list,
                ):
                    raise ValueError(
                        "Connector runtime 'files' output "
                        "must be a list."
                    )

                outputs: list[
                    dict[str, Any]
                ] = []

                for item in files:

                    if not isinstance(
                        item,
                        dict,
                    ):
                        raise ValueError(
                            "Connector runtime file output "
                            "must contain dictionaries."
                        )

                    outputs.append(
                        deepcopy(item)
                    )

                return outputs

            return [
                deepcopy(
                    runtime_result
                )
            ]

        raise ValueError(
            "Connector runtime result must be "
            "a dictionary, list of dictionaries, "
            "or None."
        )

    async def execute(
        self,
        db: AsyncSession,
        context: PipelineExecutionContext,
    ) -> ExecutorResult:

        configuration = deepcopy(
            context.pipeline_step.configuration_json
            or
            {}
        )

        connector_instance_id = (
            configuration.pop(
                "connector_instance_id",
                None,
            )
        )

        if connector_instance_id is None:

            raise ValueError(
                "connector_instance_id is required."
            )

        execution_result = await (
            connector_execution_service
            .execute(
                db=db,
                connector_instance_id=(
                    connector_instance_id
                ),
                configuration=configuration,
            )
        )

        runtime_result = (
            execution_result.get(
                "runtime_result"
            )
        )

        outputs = self._normalize_outputs(
            runtime_result
        )

        return ExecutorResult(
            metrics={
                "connector_instance_id": (
                    execution_result[
                        "connector_instance_id"
                    ]
                ),
                "connector_implementation_id": (
                    execution_result[
                        "connector_implementation_id"
                    ]
                ),
                "implementation_code": (
                    execution_result[
                        "implementation_code"
                    ]
                ),
                "output_count": len(
                    outputs
                ),
            },
            outputs=outputs,
        )


connector_executor = (
    ConnectorExecutor()
)