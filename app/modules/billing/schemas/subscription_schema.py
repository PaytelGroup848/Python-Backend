from pydantic import BaseModel
from typing import Optional


class SubscriptionPurchaseRequest(
    BaseModel
):

    plan_code: str

    provider: str

    currency: str = "INR"

    billing_cycle: str = "monthly"

    auto_renew: bool = False

    payment_metadata: Optional[dict] = None