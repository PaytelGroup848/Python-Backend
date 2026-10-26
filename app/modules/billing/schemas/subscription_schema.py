from pydantic import BaseModel
from typing import Optional, Dict, Any


class BillingDetails(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    company_name: Optional[str] = None
    gstin: Optional[str] = None


class SubscriptionPurchaseRequest(BaseModel):
    plan_code: str
    provider: str
    currency: str = "INR"
    billing_cycle: str = "monthly"
    auto_renew: bool = False
    payment_metadata: Optional[Dict[str, Any]] = None
    billing_details: Optional[BillingDetails] = None


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
