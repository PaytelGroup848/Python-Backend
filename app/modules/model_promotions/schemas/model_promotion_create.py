from datetime import datetime

from pydantic import BaseModel


class ModelPromotionCreate(
    BaseModel
):

    evaluation_job_id: int

    promotion_status: str = "PENDING"

    target_environment: str = "DEVELOPMENT"

    is_active: bool = True

    approved_by: str | None = None

    approved_at: datetime | None = None

    approval_reason: str | None = None