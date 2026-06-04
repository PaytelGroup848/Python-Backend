from pydantic import BaseModel

from typing import List


class ProviderAnalyticsResponse(
    BaseModel
):

    provider: str

    requests: int

class TopModelResponse(
    BaseModel
):

    model_name: str

    requests: int


class TopUserResponse(
    BaseModel
):

    user_id: int

    requests: int


class AnalyticsOverviewResponse(
    BaseModel
):

    total_requests: int

    average_latency_ms: float

    total_users: int

    total_models: int

    total_api_keys: int

    providers: List[
        ProviderAnalyticsResponse
    ]

    top_models: List[
        TopModelResponse
    ]

    top_users: List[
        TopUserResponse
    ]