from app.modules.billing.models.payment import (
    Payment
)

from app.modules.billing.repositories.payment_repository import (
    payment_repository
)

from app.modules.billing.constants.payment_status import (
    PENDING,
    PAID,
    FAILED,
    REFUNDED
)

from app.modules.billing.services.payment_gateway_service import (
    payment_gateway_service
)


class PaymentService:

    async def create_payment(
        self,
        db,
        user_id: int,
        provider: str,
        payment_type: str,
        amount,
        currency: str,
        invoice_id: int = None,
        subscription_id: int = None,
        gateway_order_id: str = None,
        payment_metadata: dict = None
    ):
        gateway_response = await (
            payment_gateway_service.create_payment(

                provider_name=provider,

                amount=amount,

                currency=currency,

                metadata=payment_metadata
            )
        )

        payment = Payment(

            user_id=user_id,

            invoice_id=invoice_id,

            subscription_id=subscription_id,

            provider=provider,

            payment_type=payment_type,

            amount=amount,

            currency=currency,

            status=PENDING,

            gateway_order_id=
                gateway_response.get(
                    "payment_intent_id"
                ),

            payment_metadata=
                payment_metadata
        )

        saved_payment = await (
            payment_repository.create(
                db,
                payment
            )
        )

        return {

            "payment":
                saved_payment,

            "client_secret":
                gateway_response[
                    "client_secret"
                ],

            "payment_intent_id":
                gateway_response[
                    "payment_intent_id"
                ],

            "status":
                gateway_response[
                    "status"
                ]
        }

    async def get_payment(
        self,
        db,
        payment_id: int
    ):

        return await (
            payment_repository
            .get_by_id(
                db,
                payment_id
            )
        )

    async def get_user_payments(
        self,
        db,
        user_id: int
    ):

        return await (
            payment_repository
            .get_by_user(
                db,
                user_id
            )
        )

    async def mark_paid(
        self,
        db,
        payment_id: int,
        gateway_payment_id: str
    ):

        payment = await (
            payment_repository
            .get_by_id(
                db,
                payment_id
            )
        )

        if not payment:

            return None

        payment.status = PAID

        payment.gateway_payment_id = (
            gateway_payment_id
        )

        return await (
            payment_repository
            .update(
                db,
                payment
            )
        )
    
    async def mark_paid_by_gateway_id(
        self,
        db,
        gateway_order_id: str
    ):

        payment = await (
            payment_repository
            .get_by_gateway_order_id(

                db,

                gateway_order_id
            )
        )

        if not payment:

            return None

        payment.status = PAID

        payment.gateway_payment_id = (
            gateway_order_id
        )

        return await (
            payment_repository
            .update(
                db,
                payment
            )
        )

    async def mark_failed(
        self,
        db,
        payment_id: int
    ):

        payment = await (
            payment_repository
            .get_by_id(
                db,
                payment_id
            )
        )

        if not payment:

            return None

        payment.status = FAILED

        return await (
            payment_repository
            .update(
                db,
                payment
            )
        )
    
    async def mark_refunded(
        self,
        db,
        payment_id: int
    ):

        payment = await (
            payment_repository
            .get_by_id(
                db,
                payment_id
            )
        )

        if not payment:

            return None

        payment.status = REFUNDED

        return await (
            payment_repository
            .update(
                db,
                payment
            )
        )

    async def get_by_gateway_order_id(
        self,
        db,
        gateway_order_id: str
    ):

        return await (
            payment_repository
            .get_by_gateway_order_id(
                db,
                gateway_order_id
            )
        )

    async def get_by_gateway_payment_id(
        self,
        db,
        gateway_payment_id: str
    ):

        return await (
            payment_repository
            .get_by_gateway_payment_id(
                db,
                gateway_payment_id
            )
        )


payment_service = (
    PaymentService()
)