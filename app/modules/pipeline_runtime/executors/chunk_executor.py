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

            if not input_record:
                continue

            try:

                parsed_document = ParsedDocument.model_validate(
                    input_record
                )

            except Exception as ex:

                raise ValueError(
                    f"Invalid parsed document: {ex}"
                )

            chunks = await (
                chunk_execution_service.execute(
                    parsed_document=parsed_document,
                    chunker_code=chunker_code,
                    configuration=configuration,
                )
            )

            if not chunks:
                continue

            total_chunks += len(chunks)

            for chunk in chunks:

                if not chunk.content.strip():
                    continue

                output = chunk.model_dump()

                metadata = deepcopy(
                    output.get("metadata")
                    or {}
                )

                metadata["parser_code"] = (
                    parsed_document.parser_code
                )

                metadata["chunker_code"] = (
                    chunker_code
                )

                metadata["pipeline_step"] = (
                    context.pipeline_step.step_code
                )

                metadata["file_name"] = (
                    parsed_document.file_name
                )

                metadata["mime_type"] = (
                    parsed_document.mime_type
                )

                output["metadata"] = metadata

                output["dataset_id"] = (
                    context.dataset.id
                    if context.dataset
                    else None
                )

                output["corpus_source_id"] = (
                    context.corpus_source.id
                    if context.corpus_source
                    else None
                )

                outputs.append(output)

        return ExecutorResult(
            metrics={

                "input_count": len(context.inputs),

                "output_count": len(outputs),

                "chunk_count": total_chunks,

                "pipeline_step": context.pipeline_step.step_code,

                "runtime": chunker_code,
            },
            outputs=outputs,
        )


chunk_executor = ChunkExecutor()