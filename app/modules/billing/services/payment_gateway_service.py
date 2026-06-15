from app.modules.billing.providers.provider_registry import (
    provider_registry
)


class PaymentGatewayService:

    def _get_provider(
        self,
        provider_name: str
    ):

        provider = (
            provider_registry.get(
                provider_name
            )
        )

        if not provider:

            raise ValueError(
                f"Unsupported payment provider: "
                f"{provider_name}"
            )

        return provider

    async def create_payment(
        self,
        provider_name: str,
        amount,
        currency: str,
        metadata=None
    ):

        provider = (
            self._get_provider(
                provider_name
            )
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

        provider = (
            self._get_provider(
                provider_name
            )
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

        provider = (
            self._get_provider(
                provider_name
            )
        )

        return await (
            provider.verify_webhook(

                payload,

                signature
            )
        )


payment_gateway_service = (
    PaymentGatewayService()
)