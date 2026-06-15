from datetime import datetime
from pydantic import BaseModel


class UserResponse(BaseModel):

    id: int

    name: str

    email: str

    role: str

    plan_name: str | None = None

    monthly_token_limit: int = 0

    total_tokens: int = 0

    remaining_tokens: int = 0

    is_active: bool | None = None

    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):

    users: list[UserResponse]


class UserStatusUpdate(BaseModel):

    is_active: bool

class UserPlanUpdate(BaseModel):

    plan_name: str