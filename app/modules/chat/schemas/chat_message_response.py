from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class ChatMessageResponse(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    conversation_id: int

    role: str

    content: str

    status: str

    created_at: datetime