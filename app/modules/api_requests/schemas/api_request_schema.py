from datetime import datetime

from pydantic import BaseModel


class ApiRequestResponse(BaseModel):

    id: int

    request_id: str

    user_id: int

    api_key_id: int | None = None

    model_name: str

    provider: str

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int

    latency_ms: int

    status_code: int

    created_at: datetime

    class Config:
        from_attributes = True


class ApiRequestListResponse(
    BaseModel
):

    requests: list[
        ApiRequestResponse
    ]