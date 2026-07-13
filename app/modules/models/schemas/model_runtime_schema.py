from pydantic import BaseModel

class ModelRuntime(
    BaseModel
):

    model_id: int

    model_version_id: int

    provider_id: int

    model_code: str

    model_display_name: str

    version: str

    version_display_name: str

    is_default: bool

    deployment_id: int

    deployment_name: str

    deployment_type: str

    endpoint_url: str

    max_context_window: int

    gpu_type: str | None

    gpu_count: int | None

    deployment_active: bool