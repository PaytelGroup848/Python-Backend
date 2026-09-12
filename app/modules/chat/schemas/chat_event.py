from pydantic import BaseModel


class ChatEvent(
    BaseModel
):

    request_id: str

    user_id: int

    conversation_id: int

    assistant_id: int | None = None

    message: str

    aspect_ratio: str | None = "1024x1024"
    web_search: bool | None = False