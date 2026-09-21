from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BlockType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    LIST_ITEM = "list_item"


class DocumentBlock(BaseModel):
    block_id: int
    type: BlockType
    text: Optional[str] = None
    level: Optional[int] = None                  # 1, 2, 3 for headings
    rows: Optional[List[List[str]]] = None       # 2D matrix of cell strings for tables
    list_type: Optional[str] = None              # "bullet" | "numbered"
    list_level: Optional[int] = 0                # Nesting depth: 0 = root, 1 = child, etc.


class TextTranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100000)
    target_language: str = Field(..., min_length=2, max_length=10)
    source_language: Optional[str] = "auto"


class TextTranslationResponse(BaseModel):
    status: str = "completed"
    source_language: str
    target_language: str
    original_text: str
    translated_text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class DocumentJobCreationResponse(BaseModel):
    job_id: str
    filename: str
    status: str = "queued"
    source_language: str
    target_language: str
    message: str = "Document translation job initiated"


class DocumentJobStatusResponse(BaseModel):
    job_id: str
    filename: str
    status: str  # "queued" | "parsing" | "translating" | "exporting" | "completed" | "failed"
    progress_percent: int
    source_language: str
    target_language: str
    blocks_total: int = 0
    blocks_completed: int = 0
    original_blocks: Optional[List[DocumentBlock]] = None
    translated_blocks: Optional[List[DocumentBlock]] = None
    prompt_tokens_used: int = 0
    completion_tokens_used: int = 0
    total_tokens_used: int = 0
    error_message: Optional[str] = None
    available_downloads: List[str] = []  # ["pdf", "docx"]
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class SupportedLanguageItem(BaseModel):
    code: str
    display_name: str
    native_name: str
    is_source: bool = True
    is_target: bool = True


class SupportedLanguagesResponse(BaseModel):
    languages: List[SupportedLanguageItem]
