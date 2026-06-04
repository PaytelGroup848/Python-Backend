from datetime import datetime

from pydantic import BaseModel


class CreateApiKeyRequest(BaseModel):

    name: str


class ApiKeyResponse(BaseModel):

    id: int

    name: str

    key: str

    is_active: bool

    created_at: datetime | None = None


class ApiKeyListItem(BaseModel):

    id: int

    name: str

    is_active: bool

    created_at: datetime | None = None

    last_used_at: datetime | None = None

    class Config:

        from_attributes = True


class ApiKeyListResponse(BaseModel):

    api_keys: list[ApiKeyListItem]