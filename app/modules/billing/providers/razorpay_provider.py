
import razorpay

from decimal import Decimal

from app.core.config import (
    settings
)

from app.modules.billing.providers.base_provider import (
    BasePaymentProvider
)

from app.modules.billing.utils.money import to_minor_units
from app.modules.billing.constants.payment_provider import (
    RAZORPAY
)


class RazorpayProvider(
    BasePaymentProvider
):

    def __init__(
        self
    ):

        self.client = razorpay.Client(

            auth=(

                settings.RAZORPAY_KEY_ID,

                settings.RAZORPAY_KEY_SECRET
            )
        )

    async def create_payment(
        self,
        amount,
        currency,
        metadata=None
    ):

        try:

            order = (
                self.client.order.create({

                    "amount":
                        to_minor_units(amount, currency),

                    "currency":
                        currency,

                    "notes":
                        metadata or {}
                })
            )

        except Exception as e:

            raise Exception(
                f"Razorpay order creation failed: "
                f"{str(e)}"
            )

        return {

            "provider":
                RAZORPAY,

            "payment_intent_id":
                order["id"],

            "client_secret":
                order["id"],

            "status":
                "created"
        }

    async def verify_payment(
        self,
        payload
    ):

        try:

            self.client.utility.verify_payment_signature(
                payload
            )

            return {
                "status": "verified"
            }

        except Exception as e:

            raise Exception(
                f"Razorpay signature verification failed: "
                f"{str(e)}"
            )

    async def verify_webhook(
        self,
        payload,
        signature
    ):

        try:

            self.client.utility.verify_webhook_signature(

                payload,

                signature,

                settings.RAZORPAY_WEBHOOK_SECRET
            )

            print(
                "RAZORPAY_WEBHOOK_VERIFIED"
            )

            return True

        except Exception as e:

            raise Exception(
                f"Razorpay webhook verification failed: "
                f"{str(e)}"
            )

        

    async def refund_payment(
        self,
        payment_id,
        amount=None
    ):

        try:

            refund = (
                self.client.payment.refund(

                    payment_id,

                    {

                        "amount":
                            int(
                                Decimal(str(amount))
                                * 100
                            )

                        if amount
                        else None
                    }
                )
            )

        except Exception as e:

            raise Exception(
                f"Razorpay refund failed: "
                f"{str(e)}"
            )

        return {

            "refund_id":
                refund["id"],

            "status":
                refund["status"]
        }