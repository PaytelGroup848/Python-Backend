from pydantic import BaseModel

from datetime import datetime


class ConversationCreate(
    BaseModel
):
    title: str = "New Chat"
    assistant_id: int | None = None


class ConversationResponse(
    BaseModel
):
    id: int
    title: str
    assistant_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True