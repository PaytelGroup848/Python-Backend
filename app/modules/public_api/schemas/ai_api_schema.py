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


class ImageGenerationAPIRequest(BaseModel):
    prompt: str
    model: str = "flux-1.1-pro"
    n: int = 1
    size: str = "1024x1024"
    response_format: str = "url"
    user: str | None = None