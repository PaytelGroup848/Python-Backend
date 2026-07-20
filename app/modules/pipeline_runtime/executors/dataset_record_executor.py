from copy import deepcopy
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dataset_records.schemas.dataset_record_create import (
    DatasetRecordCreate,
)
from app.modules.dataset_records.services.dataset_record_service import (
    dataset_record_service,
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


class DatasetRecordExecutor(
    BaseExecutor,
):

    async def execute(
        self,
        db: AsyncSession,
        context: PipelineExecutionContext,
    ) -> ExecutorResult:

        outputs: list[dict[str, Any]] = []

        created_count = 0

        if not context.inputs:

            return ExecutorResult(
                metrics={
                    "input_count": 0,
                    "created_count": 0,
                },
                outputs=[],
            )

        for input_record in context.inputs:

            if not input_record:
                continue

            content = input_record.get("content")

            if not content or not content.strip():
                continue

            dataset_id = input_record.get(
                "dataset_id"
            )

            if dataset_id is None:

                raise ValueError(
                    "dataset_id is required."
                )
            
            metadata = deepcopy(
                input_record.get("metadata") or {}
            )

            dataset_record = DatasetRecordCreate(

                dataset_id=dataset_id,

                corpus_source_id=input_record.get(
                    "corpus_source_id"
                ),

                record_type=input_record.get(
                    "record_type",
                    "TEXT",
                ),

                status=input_record.get(
                    "status",
                    "READY",
                ),

                input_text=input_record[
                    "content"
                ],

                output_text=input_record.get(
                    "output_text"
                ),

                metadata_json=metadata,
            )

            created = await (
                dataset_record_service
                .create_dataset_record(
                    db=db,
                    data=dataset_record,
                )
            )

            created_count += 1

            outputs.append(
                {
                    "dataset_record_id": created.id,
                    "dataset_id": created.dataset_id,
                }
            )

        return ExecutorResult(
            metrics={
                "input_count": len(
                    context.inputs
                ),
                "output_count": len(outputs),
                "created_count": created_count,
            },
            outputs=outputs,
        )


dataset_record_executor = (
    DatasetRecordExecutor()
)