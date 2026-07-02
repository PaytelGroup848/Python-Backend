from pydantic import (
    BaseModel
)


class PromptRequest(
    BaseModel
):

    workspace_runtime: dict

    user_message: str

    chat_history: list[str]

    retrieved_context: list[str]