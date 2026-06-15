from decimal import Decimal

from app.modules.billing.services.subscription_service import (
    subscription_service
)

from app.modules.billing.services.invoice_service import (
    invoice_service
)

from app.modules.billing.services.payment_service import (
    payment_service
)


class SubscriptionCheckoutService:

    async def create_subscription_checkout(
        self,
        db,
        user_id: int,
        plan_id: int,
        plan_version_id: int,
        amount: Decimal,
        currency: str,
        provider: str,
        auto_renew: bool = False,
        payment_metadata: dict | None = None
    ):
        """
        Flow:

        Subscription (pending)
                ↓
        Invoice (pending)
                ↓
        Payment (pending)
                ↓
        Return payment gateway response
        """

        # Create Subscription
        subscription = await (
            subscription_service
            .create_subscription(
            db=db,
            user_id=user_id,
            plan_id=plan_id,
            plan_version_id=plan_version_id,
            auto_renew=auto_renew
        )
    )

        # Create Invoice
        invoice = await (
            invoice_service
            .create_subscription_invoice(
                db=db,
                user_id=user_id,
                subscription_id=subscription.id,
                amount=amount,
                currency=currency,
                auto_renew=auto_renew
            )
        )

        # Create Payment
        payment_response = await (
            payment_service
            .create_payment(
                db=db,
                user_id=user_id,
                provider=provider,
                payment_type="subscription",
                amount=amount,
                currency=currency,
                invoice_id=invoice.id,
                subscription_id=subscription.id,
                payment_metadata=payment_metadata
            )
        )

        return {
            "subscription": {
                "id": subscription.id,
                "plan_name": subscription.plan_name,
                "status": subscription.status
            },
            "invoice": {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "status": invoice.status
            },
            "payment": payment_response
        }


subscription_checkout_service = (
    SubscriptionCheckoutService()
)