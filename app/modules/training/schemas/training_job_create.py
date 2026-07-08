from pydantic import (
    BaseModel,
    Field,
)


class TrainingJobCreate(
    BaseModel
):

    dataset_id: int = Field(
        gt=0
    )

    dataset_snapshot_id: int = Field(
        gt=0
    )

    training_provider_id: int = Field(
        gt=0
    )

    base_model_id: int = Field(
        gt=0
    )

    base_model_version_id: int

    training_configuration_id: int = Field(
        gt=0
    )

    training_type: str = Field(
        min_length=1,
        max_length=100,
    )

    priority: int = Field(
        default=100,
        ge=0,
    )

    created_by: str | None = Field(
        default=None,
        max_length=255,
    )