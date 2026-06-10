from decimal import Decimal
from datetime import datetime
from typing import Optional
from typing import Dict
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class CreatePaymentRequest(
    BaseModel
):

    provider: str = Field(
        min_length=1,
        max_length=50
    )

    payment_type: str = Field(
        min_length=1,
        max_length=50
    )

    amount: Decimal = Field(
        gt=0
    )

    currency: str = Field(
        min_length=3,
        max_length=10
    )

    invoice_id: Optional[int] = None

    subscription_id: Optional[int] = None

    payment_metadata: Optional[
        Dict[str, Any]
    ] = None


class PaymentResponse(
    BaseModel
):

    id: int

    user_id: int

    invoice_id: Optional[int]

    subscription_id: Optional[int]

    provider: str

    payment_type: str

    amount: Decimal

    currency: str

    status: str

    gateway_order_id: Optional[str]

    gateway_payment_id: Optional[str]

    payment_metadata: Optional[
        Dict[str, Any]
    ]

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class PaymentWebhookPayload(
    BaseModel
):

    provider: str

    gateway_order_id: Optional[
        str
    ] = None

    gateway_payment_id: Optional[
        str
    ] = None

    payment_metadata: Optional[
        Dict[str, Any]
    ] = None

    payload: Optional[
        Dict[str, Any]
    ] = None


class PaymentListResponse(
    BaseModel
):

    payments: list[
        PaymentResponse
    ]

    total: int

class PaymentGatewayResponse(
    BaseModel
):

    payment: PaymentResponse

    client_secret: str

    payment_intent_id: str

    status: str