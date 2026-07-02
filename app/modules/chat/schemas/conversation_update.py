from pydantic import (
    BaseModel,
    Field
)


class ConversationUpdate(
    BaseModel
):

    title: str | None = Field(
        default=None,
        max_length=255
    )

    pinned: bool | None = None

    archived: bool | None = None