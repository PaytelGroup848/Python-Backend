from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class KnowledgeBaseDocumentResponse(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    knowledge_base_id: int

    file_name: str

    file_path: str

    mime_type: str | None = None

    file_size: int | None = None

    status: str

    error_message: str | None = None

    is_active: bool

    created_at: datetime

    updated_at: datetime