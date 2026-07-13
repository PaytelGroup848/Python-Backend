from pydantic import BaseModel

from app.modules.conversation_runtime.schemas.conversation_context import (
    ConversationContext,
)

from app.modules.workspace_runtime.schemas.workspace_runtime_schema import (
    WorkspaceRuntime,
)

from app.modules.models.schemas.inference_runtime_schema import (
    InferenceRuntime,
)


class ConversationExecutionContext(
    BaseModel
):

    conversation: ConversationContext

    workspace: WorkspaceRuntime

    inference: InferenceRuntime