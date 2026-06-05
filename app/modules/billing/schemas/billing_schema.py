from pydantic import BaseModel


class BillingOverviewResponse(
    BaseModel
):

    total_cost: float

    total_tokens: int

    total_requests: int

    provider_breakdown: list

    model_breakdown: list


class UserBillingResponse(
    BaseModel
):

    user_id: int

    total_cost: float

    total_tokens: int

    total_requests: int