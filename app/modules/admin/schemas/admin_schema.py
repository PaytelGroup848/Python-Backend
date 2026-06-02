from pydantic import BaseModel


class DashboardResponse(BaseModel):

    total_users: int

    total_conversations: int

    total_messages: int

    active_providers: int

    active_workers: int