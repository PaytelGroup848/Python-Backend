from pydantic import BaseModel


class WorkspaceRuntime(
    BaseModel
):

    workspace_id: int

    workspace_name: str

    workspace_slug: str

    model_release_id: int

    knowledge_base_ids: list[int]

    assistant_id: int | None = None

    tool_ids: list[int]

    system_prompt: str | None = None