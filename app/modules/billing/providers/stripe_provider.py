import stripe

from app.core.config import (
    settings
)

from app.modules.billing.providers.base_provider import (
    BasePaymentProvider
)


stripe.api_key = (
    settings.STRIPE_SECRET_KEY
)


class StripeProvider(
    BasePaymentProvider
):

    async def create_payment(
        self,
        amount,
        currency,
        metadata=None
    ):

        intent = (
            stripe.PaymentIntent.create(

                amount=int(
                    amount * 100
                ),

                currency=currency,

                metadata=
                    metadata or {}
            )
        )

        return {

            "provider":
                "stripe",

            "client_secret":
                intent.client_secret,

            "payment_intent_id":
                intent.id,

            "status":
                intent.status
        }

    async def verify_payment(
        self,
        payload
    ):

        payment_intent_id = (
            payload.get(
                "payment_intent_id"
            )
        )

        payment = (
            stripe.PaymentIntent.retrieve(
                payment_intent_id
            )
        )

        return {

            "payment_id":
                payment.id,

            "status":
                payment.status
        }

    async def refund_payment(
        self,
        payment_id,
        amount=None
    ):

        refund = (
            stripe.Refund.create(

                payment_intent=
                    payment_id,

                amount=(
                    int(amount * 100)
                    if amount
                    else None
                )
            )
        )

        return {

            "refund_id":
                refund.id,

            "status":
                refund.status
        }