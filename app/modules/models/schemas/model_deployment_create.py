from pydantic import (
    BaseModel,
    Field,
)


class ModelDeploymentCreate(
    BaseModel,
):

    model_version_id: int

    deployment_name: str = Field(
        min_length=1,
        max_length=255,
    )

    deployment_type: str = Field(
        min_length=1,
        max_length=100,
    )

    endpoint_url: str = Field(
        min_length=1,
        max_length=500,
    )

    max_context_window: int = Field(
        gt=0,
    )

    gpu_type: str | None = None

    gpu_count: int | None = Field(
        default=None,
        ge=1,
    )