from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class EvaluationJobCreate(
    BaseModel
):

    artifact_id: int = Field(
        gt=0,
    )

    dataset_version_id: int = Field(
        gt=0,
    )

    evaluation_type: str = Field(
        min_length=1,
        max_length=100,
    )

    runtime_configuration: dict[str, Any] = Field(
        default_factory=dict,
    )

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )