from pydantic import BaseModel


class AssistantRuntime(
    BaseModel
):

    assistant_id: int

    assistant_name: str

    assistant_code: str

    system_prompt: str | None

    knowledge_base_ids: list[int]

    model_id: int | None = None

    temperature: float = 0.2

    top_p: float = 0.95

    max_tokens: int = 4000

    context_window: int = 8000

    memory_enabled: bool = True

    rag_enabled: bool = True

    cag_enabled: bool = False

    tool_calling_enabled: bool = False

    provider_id: int | None = None

    model_id: int | None = None

    model_version_id: int | None = None

    model_code: str | None = None

    model_display_name: str | None = None

    version: str | None = None

    version_display_name: str | None = None