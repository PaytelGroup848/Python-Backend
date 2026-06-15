from app.modules.billing.providers.base_provider import (
    BasePaymentProvider
)


class PayPalProvider(
    BasePaymentProvider
):

    async def create_payment(
        self,
        amount,
        currency,
        metadata=None
    ):

        return {
            "provider": "paypal",
            "status": "created",
            "payment_id": ""
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