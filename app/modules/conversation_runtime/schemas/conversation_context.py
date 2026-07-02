from pydantic import BaseModel


class ConversationResponse(
    BaseModel
):

    conversation_id: int

    prompt: str

    history: list[str]