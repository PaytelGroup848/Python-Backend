from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict

from app.modules.assistants.schemas.assistant_config_schema import (
    AssistantConfigResponse,
)


class AssistantCreate(BaseModel):

    name: str

    code: str

    description: str | None = None

    system_prompt: str | None = None


class AssistantResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    name: str

    code: str

    description: str | None = None

    system_prompt: str | None = None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    config: AssistantConfigResponse | None = None

    icon: str | None = None

    color: str | None = None

    supports_documents: bool = False

    supports_voice: bool = False

    supports_web_search: bool = False

    supports_tools: bool = False