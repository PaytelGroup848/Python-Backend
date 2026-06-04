from pydantic import BaseModel


class TopModelResponse(BaseModel):

    model_name: str

    tokens: int


class TopUserResponse(BaseModel):

    user_id: int

    tokens: int


class UsageOverviewResponse(BaseModel):

    total_tokens: int

    prompt_tokens: int

    completion_tokens: int

    estimated_cost: float

    top_models: list[TopModelResponse]

    top_users: list[TopUserResponse]