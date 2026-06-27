from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict
)


class ModelResponse(
    BaseModel
):

    id: int

    provider_id: int

    code: str

    display_name: str

    description: str | None = None

    status: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ModelListResponse(
    BaseModel
):

    models: list[
        ModelResponse
    ]


class CreateModelRequest(
    BaseModel
):

    provider_id: int

    code: str

    display_name: str

    description: str | None = None


class UpdateModelRequest(
    BaseModel
):

    provider_id: int | None = None

    display_name: str | None = None

    description: str | None = None

    status: str | None = None

    is_active: bool | None = None