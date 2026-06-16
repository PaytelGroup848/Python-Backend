from pydantic import BaseModel


class DashboardResponse(BaseModel):

    total_users: int

    active_users: int

    active_subscriptions: int

    total_requests: int

    total_tokens: int

    monthly_revenue: float

    active_providers: int

    active_workers: int