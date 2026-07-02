from pydantic import (
    BaseModel,
    Field
)


class ConversationCreate(
    BaseModel
):

    workspace_id: int

    assistant_id: int | None = None

    title: str = Field(
        min_length=1,
        max_length=255
    )