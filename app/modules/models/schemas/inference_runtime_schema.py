from pydantic import BaseModel


class InferenceRuntime(
    BaseModel
):
    
    model_id: int

    provider_id: int

    model_code: str

    model_display_name: str

    model_version: str

    deployment_id: int

    model_version_id: int

    deployment_name: str

    deployment_type: str

    endpoint_url: str

    max_context_window: int

    gpu_type: str | None = None

    gpu_count: int | None = None