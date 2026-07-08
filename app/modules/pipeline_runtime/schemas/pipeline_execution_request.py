from pydantic import (
    BaseModel,
    Field
)

from app.shared.enums.trigger_type import (
    TriggerType
)


class PipelineExecutionRequest(
    BaseModel
):

  
    pipeline_id: int

    dataset_id: int | None = None

    corpus_source_id: int | None = None

    trigger_type: TriggerType = TriggerType.API

    execution_metadata: dict = Field(
        default_factory=dict
    )