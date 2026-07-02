from pydantic import (
    BaseModel
)


class InferenceResponse(
    BaseModel
):

    text: str

    finish_reason: str

    prompt_tokens: int

    generated_tokens: int

    total_tokens: int

    latency_ms: float