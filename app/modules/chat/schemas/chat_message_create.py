from pydantic import (
    BaseModel,
    Field
)


class ChatMessageCreate(
    BaseModel
):

    conversation_id: int

    content: str = Field(
        min_length=1
    )