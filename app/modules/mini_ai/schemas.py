from datetime import datetime
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.mini_ai.security import normalize_domain

MAX_MINI_AIS_PER_USER = 5
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_CHUNKS_PER_MINI_AI = 200
ALLOWED_EXTENSIONS = {".txt", ".csv", ".pdf", ".docx", ".xlsx"}
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,62}$")


class QAPair(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    answer: str = Field(..., min_length=1, max_length=4000)


class MiniAIResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    description: str | None = None
    system_prompt: str | None = None
    is_active: bool
    is_custom: bool
    owner_user_id: int | None = None
    knowledge_base_id: int | None = None
    chunks_count: int = 0
    share_slug: str | None = None
    is_public: bool = False
    strict_rag: bool = False
    allowed_domains: list[str] | None = None
    welcome_message: str | None = None
    created_at: datetime


class MiniAIUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    system_prompt: str | None = Field(default=None, min_length=1, max_length=4000)
    strict_rag: bool | None = None
    is_public: bool | None = None
    share_slug: str | None = Field(default=None, max_length=64)
    allowed_domains: list[str] | None = None
    welcome_message: str | None = Field(default=None, max_length=1000)

    @field_validator("share_slug")
    @classmethod
    def validate_slug(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip().lower()
        if not cleaned:
            return None
        if not _SLUG_RE.match(cleaned):
            raise ValueError(
                "share_slug must be 3-63 lowercase letters, numbers, or hyphens."
            )
        return cleaned

    @field_validator("allowed_domains")
    @classmethod
    def validate_domains(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        return list(dict.fromkeys(normalize_domain(item) for item in v if item.strip()))


class MiniAIDocumentItem(BaseModel):
    id: int
    file_name: str
    mime_type: str | None = None
    status: str
    error_message: str | None = None
    chunk_count: int = 0
    created_at: datetime


class MiniAIDocumentsResponse(BaseModel):
    documents: list[MiniAIDocumentItem]
    chunks_used: int
    chunk_limit: int = MAX_CHUNKS_PER_MINI_AI
    remaining_chunks: int


class MiniAILeadItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visitor_name: str
    visitor_contact: str
    first_question: str | None = None
    created_at: datetime


class MiniAIGapItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    hit_count: int
    resolved: bool
    created_at: datetime
    updated_at: datetime


class MiniAIInsightsResponse(BaseModel):
    leads: list[MiniAILeadItem]
    gaps: list[MiniAIGapItem]
    total_leads: int
    total_gaps: int


class TrainGapRequest(BaseModel):
    answer: str = Field(..., min_length=1, max_length=4000)


class PublicBotInfoResponse(BaseModel):
    name: str
    description: str | None = None
    welcome_message: str | None = None
    strict_rag: bool


class PublicChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=2000)


class PublicChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1500)
    history: list[PublicChatMessage] = Field(default_factory=list, max_length=6)


class PublicChatResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    grounded: bool = True
    fallback_triggered: bool = False


class PublicLeadCreateRequest(BaseModel):
    visitor_name: str = Field(..., min_length=1, max_length=120)
    visitor_contact: str = Field(..., min_length=3, max_length=160)
    first_question: str | None = Field(default=None, max_length=1000)
