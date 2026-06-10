from decimal import Decimal

from pydantic import (
    BaseModel,
    Field
)


class WalletCreditRequest(
    BaseModel
):

    amount: Decimal = Field(
        gt=0
    )