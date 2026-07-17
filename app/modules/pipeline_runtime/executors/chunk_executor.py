from copy import deepcopy
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ingestion.schemas.parsed_document import (
    ParsedDocument,
)

from app.modules.ingestion.services.chunk_execution_service import (
    chunk_execution_service,
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


class ChunkExecutor(
    BaseExecutor,
):

    async def execute(
        self,
        db: AsyncSession,
        context: PipelineExecutionContext,
    ) -> ExecutorResult:

        configuration = deepcopy(
            context.pipeline_step.configuration_json
            or {}
        )

        chunker_code = (
            context.pipeline_step.runtime_code
        )

        if not chunker_code:
            raise ValueError(
                "Chunk step runtime_code is required."
            )

        outputs: list[
            dict[str, Any]
        ] = []

        total_chunks = 0

        for input_record in context.inputs:

            parsed_document = (
                ParsedDocument.model_validate(
                    input_record
                )
            )

            chunks = await (
                chunk_execution_service.execute(
                    parsed_document=parsed_document,
                    chunker_code=chunker_code,
                    configuration=configuration,
                )
            )

            total_chunks += len(chunks)

            for chunk in chunks:

                output = chunk.model_dump()

                metadata = deepcopy(
                    output.get("metadata")
                    or {}
                )

                metadata["parser_code"] = (
                    parsed_document.parser_code
                )

                metadata["file_name"] = (
                    parsed_document.file_name
                )

                metadata["mime_type"] = (
                    parsed_document.mime_type
                )

                output["metadata"] = metadata

                outputs.append(output)

        return ExecutorResult(
            metrics={
                "input_count": len(
                    context.inputs
                ),
                "chunk_count": total_chunks,
            },
            outputs=outputs,
        )


chunk_executor = ChunkExecutor()