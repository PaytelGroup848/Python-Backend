from datetime import datetime

from pydantic import BaseModel


class TrainingProviderResponse(
    BaseModel
):

    id: int

    code: str

    display_name: str

    provider_type: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True