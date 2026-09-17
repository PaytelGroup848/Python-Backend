from decimal import Decimal
from typing import Optional

from pydantic import (
    BaseModel,
    Field
)


class WalletCreditRequest(
    BaseModel
):

    amount: Decimal = Field(
        gt=0,
        le=Decimal("100000.00")
    )

    target_user_id: Optional[int] = None

    reason: Optional[str] = Field(
        default="Manual admin credit",
        max_length=255
    )