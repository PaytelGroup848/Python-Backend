from datetime import datetime

from pydantic import BaseModel


class ModelPromotionResponse(
    BaseModel
):

    id: int

    evaluation_job_id: int

    promotion_status: str

    approved_by: str | None

    approval_reason: str | None

    created_at: datetime

    class Config:

        from_attributes = True