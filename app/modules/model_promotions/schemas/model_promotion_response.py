from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict
)


class ModelPromotionResponse(
    BaseModel
):

    id: int

    evaluation_job_id: int

    promotion_status: str

    target_environment: str

    is_active: bool

    approved_by: str | None

    approved_at: datetime | None

    approval_reason: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )