from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class ConversationResponse(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    workspace_id: int

    assistant_id: int | None

    title: str

    status: str

    pinned: bool

    archived: bool

    last_message_at: datetime | None

    created_at: datetime