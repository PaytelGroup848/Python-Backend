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


class VerifyPaymentRequest(
    BaseModel
):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
