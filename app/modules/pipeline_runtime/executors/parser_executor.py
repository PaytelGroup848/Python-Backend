from copy import deepcopy
from pathlib import Path

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

from app.modules.ingestion.services.parser_execution_service import (
    parser_execution_service,
)


class ParserExecutor(
    BaseExecutor,
):

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

        outputs: list[dict] = []

        for input_record in context.inputs:

            file_path_value = (
                input_record.get("path")
                or
                input_record.get("file_path")
            )

            if not file_path_value:

                raise ValueError(
                    "Parser input requires a file path."
                )

            mime_type = input_record.get(
                "mime_type"
            )

            parsed_document = await (
                parser_execution_service
                .execute(
                    file_path=Path(
                        file_path_value
                    ),
                    mime_type=mime_type,
                    configuration=configuration,
                )
            )

            output = deepcopy(
                parsed_document
            )

            source_metadata = deepcopy(
                output.get("metadata")
                or
                {}
            )

            source_metadata[
                "source_path"
            ] = file_path_value

            if input_record.get("size_bytes") is not None:
                source_metadata[
                    "source_size_bytes"
                ] = input_record[
                    "size_bytes"
                ]

            output["metadata"] = (
                source_metadata
            )

            if context.dataset is not None:
                output["dataset_id"] = (
                    context.dataset.id
                )

            if context.corpus_source is not None:
                output["corpus_source_id"] = (
                    context.corpus_source.id
                )

            outputs.append(
                output
            )

        return ExecutorResult(
            metrics={
                "input_count": len(
                    context.inputs
                ),
                "parsed_document_count": len(
                    outputs
                ),
            },
            outputs=outputs,
        )


parser_executor = (
    ParserExecutor()
)