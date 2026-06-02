from pydantic import BaseModel


class ProviderStatus(BaseModel):
    name: str
    status: str
    latency_ms: int


class ProviderListResponse(BaseModel):
    providers: list[ProviderStatus]