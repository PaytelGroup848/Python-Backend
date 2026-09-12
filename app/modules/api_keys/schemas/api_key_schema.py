from datetime import datetime
from pydantic import BaseModel


class CreateApiKeyRequest(BaseModel):
    name: str


class CreateApiKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    prefix: str | None = None
    is_active: bool
    created_at: datetime | None = None


class ApiKeyListItem(BaseModel):
    id: int
    name: str
    prefix: str | None = None
    key: str | None = None
    is_active: bool
    created_at: datetime | None = None
    last_used_at: datetime | None = None

    class Config:
        from_attributes = True


class ApiKeyListResponse(BaseModel):
    api_keys: list[ApiKeyListItem]


class UserApiKeyUsageResponse(BaseModel):
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    monthly_tokens: int = 0
    token_limit: int = 100000
    remaining_tokens: int = 100000
    estimated_cost: float = 0.0
    plan_name: str = "free"
