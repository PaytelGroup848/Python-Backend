from decimal import Decimal
from typing import Union

# Standard ISO-4217 currency decimal places
CURRENCY_DECIMALS = {
    "INR": 2,
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "JPY": 0,
}


def to_minor_units(amount: Union[Decimal, float, int, str], currency: str) -> int:
    """
    Converts a currency amount to its exact integer minor units (e.g. paise, cents).
    Strictly enforces supported currencies and avoids floating point inaccuracies.
    """
    if not currency:
        raise ValueError("Currency must be specified")

    curr = currency.upper().strip()
    if curr not in CURRENCY_DECIMALS:
        raise ValueError(f"Unsupported currency: {currency}. Supported: {list(CURRENCY_DECIMALS.keys())}")

    dec_scale = CURRENCY_DECIMALS[curr]
    dec_amount = Decimal(str(amount))
    multiplier = Decimal(10 ** dec_scale)

    return int(round(dec_amount * multiplier))
