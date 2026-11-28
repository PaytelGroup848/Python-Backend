from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, model_validator


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    images: list[dict[str, Any]] | None = None
    sources: list[dict[str, Any]] | None = None
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _extract_metadata(cls, data: Any) -> Any:
        if isinstance(data, dict):
            meta = data.get("metadata_json")
            if isinstance(meta, dict):
                data.setdefault("images", meta.get("images"))
                data.setdefault("sources", meta.get("sources"))
            return data

        meta = getattr(data, "metadata_json", None)
        if isinstance(meta, dict):
            return {
                "id": data.id,
                "role": data.role,
                "content": data.content,
                "images": meta.get("images"),
                "sources": meta.get("sources"),
                "created_at": data.created_at,
            }
        return data