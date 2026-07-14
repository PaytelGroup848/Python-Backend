from pydantic import (
    BaseModel
)
from app.modules.workspace_runtime.schemas.workspace_runtime_schema import (
    WorkspaceRuntime,
)

class PromptRequest(
    BaseModel
):

    workspace_runtime: WorkspaceRuntime

    user_message: str

    chat_history: list[str]

    retrieved_context: list[str]