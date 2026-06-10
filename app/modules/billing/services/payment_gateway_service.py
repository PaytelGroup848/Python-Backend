from app.modules.billing.providers.provider_registry import (
    provider_registry
)


class PaymentGatewayService:

    async def create_payment(
        self,
        provider_name: str,
        amount,
        currency: str,
        metadata=None
    ):

        provider = provider_registry.get(
            provider_name
        )

        if not provider:

            raise ValueError(
                f"Unsupported payment provider: "
                f"{provider_name}"
            )

        return await (
            provider.create_payment(

                amount=amount,

                currency=currency,

                metadata=metadata
            )
        )

    async def verify_payment(
        self,
        provider_name: str,
        payload
    ):

        provider = provider_registry.get(
            provider_name
        )

        if not provider:

            raise ValueError(
                f"Unsupported payment provider: "
                f"{provider_name}"
            )

        return await (
            provider.verify_payment(
                payload
            )
        )

    async def verify_webhook(
        self,
        provider_name: str,
        payload,
        signature
    ):

        provider = provider_registry.get(
            provider_name
        )

        if not provider:

            raise ValueError(
                f"Unsupported payment provider: "
                f"{provider_name}"
            )

        return await (
            provider.verify_webhook(

                payload,

                signature
            )
        )

    async def refund_payment(
        self,
        provider_name: str,
        payment_id: str,
        amount=None
    ):

        provider = provider_registry.get(
            provider_name
        )

        if not provider:

            raise ValueError(
                f"Unsupported payment provider: "
                f"{provider_name}"
            )

        return await (
            provider.refund_payment(

                payment_id,

                amount
            )
        )


payment_gateway_service = (
    PaymentGatewayService()
)