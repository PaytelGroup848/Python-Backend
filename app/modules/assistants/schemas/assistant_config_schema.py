from pydantic import BaseModel


class AssistantConfigCreate(

    BaseModel
):

    assistant_id: int

    model_id: int | None = None

    temperature: float = 0.2

    top_p: float = 0.95

    max_tokens: int = 4000

    context_window: int = 8000

    memory_enabled: bool = True

    rag_enabled: bool = True

    cag_enabled: bool = False

    tool_calling_enabled: bool = False


class AssistantConfigResponse(

    AssistantConfigCreate
):

    id: int

    class Config:

        from_attributes = True