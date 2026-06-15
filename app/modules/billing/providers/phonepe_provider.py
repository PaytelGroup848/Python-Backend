from app.modules.billing.providers.base_provider import (
    BasePaymentProvider
)


class PhonePeProvider(
    BasePaymentProvider
):

    async def create_payment(
        self,
        amount,
        currency,
        metadata=None
    ):

        return {
            "provider": "phonepe",
            "status": "created",
            "merchant_transaction_id": ""
        }

    async def verify_payment(
        self,
        payload
    ):

        return True

    async def verify_webhook(
        self,
        payload,
        signature
    ):

        return True