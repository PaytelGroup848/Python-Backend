from pydantic import BaseModel


class ModelGenerationRequest(
    BaseModel
):

    prompt: str

    temperature: float | None = None

    max_tokens: int | None = None