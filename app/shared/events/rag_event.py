from pydantic import BaseModel


class RAGEvent(
    BaseModel
):

    request_id: str

    query: str

    user_id: int

    conversation_id: int