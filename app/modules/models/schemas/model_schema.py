from datetime import datetime

from pydantic import BaseModel


class ModelResponse(BaseModel):

    id: int

    model_name: str

    provider: str

    description: str | None = None

    is_active: bool

    created_at: datetime

    class Config:
        from_attributes = True


class ModelListResponse(
    BaseModel
):

    models: list[
        ModelResponse
    ]


class CreateModelRequest(
    BaseModel
):

    model_name: str

    provider: str

    description: str | None = None

class UpdateModelRequest(
    BaseModel
):

    provider: str | None = None

    description: str | None = None

    is_active: bool | None = None