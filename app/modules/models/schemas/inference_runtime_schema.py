from pydantic import BaseModel


class InferenceRuntime(
    BaseModel
):

    deployment_id: int

    model_version_id: int

    deployment_name: str

    deployment_type: str

    endpoint_url: str

    max_context_window: int

    gpu_type: str | None = None

    gpu_count: int | None = None