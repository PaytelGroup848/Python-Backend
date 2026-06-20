from pydantic import BaseModel


class ModelGenerationRequest(
    BaseModel
):

    prompt: str

    temperature: float = 0.2

    max_tokens: int = 4000