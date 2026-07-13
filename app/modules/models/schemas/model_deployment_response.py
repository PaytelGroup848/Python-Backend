from datetime import datetime

from pydantic import (
    BaseModel,
)


class ModelDeploymentResponse(
    BaseModel,
):

    id: int

    model_version_id: int

    deployment_name: str

    deployment_type: str

    endpoint_url: str

    max_context_window: int

    gpu_type: str | None

    gpu_count: int | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }