from pydantic import BaseModel


class AssistantRuntime(
    BaseModel
):

    assistant_id: int

    assistant_name: str

    assistant_code: str

    system_prompt: str | None

    knowledge_base_ids: list[int]

    temperature: float | None = None

    top_p: float | None = None

    max_tokens: int | None = None

    context_window: int | None = None

    memory_enabled: bool | None = None

    rag_enabled: bool | None = None

    cag_enabled: bool | None = None

    tool_calling_enabled: bool | None = None

    provider_id: int | None = None

    model_id: int | None = None

    model_version_id: int | None = None

    model_code: str | None = None

    model_display_name: str | None = None

    version: str | None = None

    version_display_name: str | None = None

    deployment_id: int | None = None

    deployment_name: str | None = None

    deployment_type: str | None = None