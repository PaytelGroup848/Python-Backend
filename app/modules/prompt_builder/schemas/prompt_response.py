from pydantic import (
    BaseModel
)


class PromptResponse(
    BaseModel
):

    system_prompt: str

    user_prompt: str