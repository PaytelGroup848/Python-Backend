from pydantic import BaseModel


class ChatEvent(
    BaseModel
):

    request_id: str

    user_id: int

    conversation_id: int

    message: str