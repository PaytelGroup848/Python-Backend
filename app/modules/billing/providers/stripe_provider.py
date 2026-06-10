import stripe

from decimal import Decimal
from app.core.config import (
    settings
)

from app.modules.billing.providers.base_provider import (
    BasePaymentProvider
)

from app.modules.billing.constants.payment_provider import (
    STRIPE
)



class StripeProvider(
    BasePaymentProvider
):
    
    def __init__(
        self
    ):

        stripe.api_key = (
            settings.STRIPE_SECRET_KEY
        )

    async def create_payment(
        self,
        amount,
        currency,
        metadata=None
    ):

        try:

            intent = (
                stripe.PaymentIntent.create(

                    amount=int(
                        Decimal(str(amount))
                        * 100
                    ),

                    currency=currency,

                    metadata=
                        metadata or {}
                )
            )

        except stripe.error.StripeError as e:

            raise Exception(
                f"Stripe payment creation failed: {str(e)}"
            )

        return {

            "provider":
                STRIPE,

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

        try:

            payment = (
                stripe.PaymentIntent.retrieve(
                    payment_intent_id
                )
            )

        except stripe.error.StripeError as e:

            raise Exception(
                f"Stripe payment verification failed: {str(e)}"
            )

        return {

            "payment_id":
                payment.id,

            "status":
                payment.status
        }
    
    async def verify_webhook(
        self,
        payload,
        signature
    ):

        try:

            event = (
                stripe.Webhook.construct_event(

                    payload,

                    signature,

                    settings.STRIPE_WEBHOOK_SECRET
                )
            )

            return event

        except Exception as e:

            raise Exception(
                f"Stripe webhook verification failed: "
                f"{str(e)}"
            )

    async def refund_payment(
        self,
        payment_id,
        amount=None
    ):

        try:

            refund = (
                stripe.Refund.create(

                    payment_intent=
                        payment_id,

                    amount=(

                        int(
                            Decimal(str(amount))
                            * 100
                        )

                        if amount
                        else None
                    )
                )
            )

        except stripe.error.StripeError as e:

            raise Exception(
                f"Stripe refund failed: {str(e)}"
            )

        return {

            "refund_id":
                refund.id,

            "status":
                refund.status
        }