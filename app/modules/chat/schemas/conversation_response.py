from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


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

    message_count: int

    last_message_at: datetime | None

    created_at: datetime

    updated_at: datetime