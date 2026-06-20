from pydantic import BaseModel


class ModelPromotionCreate(
    BaseModel
):

    evaluation_job_id: int

    promotion_status: str = "pending"

    approved_by: str | None = None

    approval_reason: str | None = None