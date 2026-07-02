from pydantic import BaseModel


class ConversationRequest(
    BaseModel
):

    conversation_id: int

    user_message: str

    workspace_id: int