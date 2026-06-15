from app.modules.billing.providers.base_provider import (
    BasePaymentProvider
)

class CashfreeProvider(
    BasePaymentProvider
):

    async def create_payment(
        self,
        amount,
        currency,
        metadata=None
    ):

        return {
            "provider": "cashfree",
            "status": "created",
            "payment_session_id": "",
            "order_id": ""
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