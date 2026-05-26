from pydantic import BaseModel


class ChatEvent(
    BaseModel
):

    request_id: str

    user_id: str

    conversation_id: str

    query: str
