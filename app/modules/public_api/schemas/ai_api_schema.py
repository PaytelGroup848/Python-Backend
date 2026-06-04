from pydantic import BaseModel


class ChatMessage(BaseModel):

    role: str

    content: str


class ChatCompletionRequest(
    BaseModel
):

    model: str

    messages: list[ChatMessage]


class ChatCompletionResponse(
    BaseModel
):

    id: str

    object: str

    model: str

    choices: list