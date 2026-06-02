# app/modules/admin/schemas/user_schema.py

from datetime import datetime
from pydantic import BaseModel


class UserResponse(BaseModel):

    id: int
    name: str
    email: str
    role: str

    is_active: bool | None = None

    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):

    users: list[UserResponse]