from pydantic import (
    BaseModel,
    Field,
)

from app.modules.conversation_runtime.schemas.conversation_context import (
    ConversationContext,
)


class InferenceRequest(
    BaseModel
):

    context: ConversationContext

    max_new_tokens: int = Field(
        default=512,
        ge=1,
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
    )

    top_p: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
    )

    top_k: int = Field(
        default=50,
        ge=1,
    )

    repetition_penalty: float = Field(
        default=1.1,
        ge=1.0,
    )

    stream: bool = False