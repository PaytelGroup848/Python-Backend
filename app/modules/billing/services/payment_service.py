import logging
from decimal import Decimal
from datetime import datetime, timedelta
import uuid
from fastapi import HTTPException
from sqlalchemy import select

from app.modules.billing.models.payment import (
    Payment
)
from app.modules.billing.models.invoice import (
    Invoice
)
from app.modules.billing.models.subscription import (
    Subscription
)
from app.modules.billing.repositories.payment_repository import (
    payment_repository
)
from app.modules.billing.constants.payment_status import (
    PENDING,
    PAID,
    FAILED
)
from app.modules.billing.services.payment_gateway_service import (
    payment_gateway_service
)
from app.modules.billing.utils.money import to_minor_units

logger = logging.getLogger(__name__)


class PaymentService:

    async def create_payment(
        self,
        db,
        user_id: int,
        provider: str,
        payment_type: str,
        amount,
        currency: str,
        payment_method: str = None,
        invoice_id: int = None,
        subscription_id: int = None,
        gateway_order_id: str = None,
        payment_metadata: dict = None
    ):
        provider_clean = (provider or "").lower().strip()
        if provider_clean not in ["razorpay", "stripe"]:
            raise ValueError(f"Unsupported payment provider: '{provider}'")

        payment_type_clean = (payment_type or "").lower().strip()
        if payment_type_clean not in ["subscription", "invoice", "wallet"]:
            raise ValueError(f"Invalid payment_type: '{payment_type}'")

        # Conflict rejection: wallet cannot be combined with subscription or invoice
        if payment_type_clean == "wallet":
            if subscription_id is not None or invoice_id is not None:
                raise ValueError("Wallet recharge cannot be combined with subscription or invoice IDs")
            if not currency:
                raise ValueError("Currency is required for wallet recharge")
            if currency.upper() not in ["INR", "USD"]:
                raise ValueError(f"Currency '{currency}' is not supported for wallet recharge")

            dec_amount = Decimal(str(amount))
            if dec_amount < Decimal("10.00") or dec_amount > Decimal("50000.00"):
                raise ValueError("Wallet recharge amount must be between 10.00 and 50,000.00")
            target_invoice = None
        else:
            # Subscription / Invoice flow: enforce deterministic resolution and DB authoritative snapshot
            target_invoice = None

            if invoice_id is not None:
                inv_stmt = select(Invoice).where(Invoice.id == invoice_id).with_for_update()
                inv_res = await db.execute(inv_stmt)
                target_invoice = inv_res.scalar_one_or_none()

                if not target_invoice:
                    raise ValueError(f"Invoice {invoice_id} not found")
                if target_invoice.user_id != user_id:
                    raise PermissionError(f"Invoice {invoice_id} does not belong to user {user_id}")
                if target_invoice.status != "pending":
                    raise ValueError(f"Invoice {invoice_id} has status '{target_invoice.status}', expected 'pending'")
                if subscription_id is not None and target_invoice.subscription_id != subscription_id:
                    raise ValueError(f"Invoice {invoice_id} does not match subscription {subscription_id}")

            elif subscription_id is not None:
                sub_stmt = select(Subscription).where(Subscription.id == subscription_id).with_for_update()
                sub_res = await db.execute(sub_stmt)
                target_sub = sub_res.scalar_one_or_none()

                if not target_sub:
                    raise ValueError(f"Subscription {subscription_id} not found")
                if target_sub.user_id != user_id:
                    raise PermissionError(f"Subscription {subscription_id} does not belong to user {user_id}")
                if target_sub.status != "pending":
                    raise ValueError(f"Subscription {subscription_id} has status '{target_sub.status}', expected 'pending'")

                # Deterministically select the latest pending invoice for this subscription
                det_stmt = (
                    select(Invoice)
                    .where(
                        Invoice.subscription_id == subscription_id,
                        Invoice.user_id == user_id,
                        Invoice.status == "pending"
                    )
                    .order_by(Invoice.id.desc())
                    .with_for_update()
                )
                det_res = await db.execute(det_stmt)
                target_invoice = det_res.scalars().first()

                if not target_invoice:
                    raise ValueError(f"No pending payable invoice found for subscription {subscription_id}")

            if target_invoice:
                # Immutable binding to exact invoice
                invoice_id = target_invoice.id
                subscription_id = target_invoice.subscription_id
                # DB Authoritative Price & Currency snapshot (completely overrides any client-sent amount)
                amount = target_invoice.amount
                currency = target_invoice.currency

                # Concurrent checkout duplicate order protection:
                # If a valid PENDING payment order for this exact invoice was created within the last 15 mins, reuse it
                fifteen_mins_ago = datetime.utcnow() - timedelta(minutes=15)
                check_stmt = (
                    select(Payment)
                    .where(
                        Payment.invoice_id == target_invoice.id,
                        Payment.status == PENDING,
                        Payment.created_at >= fifteen_mins_ago,
                        Payment.gateway_order_id.isnot(None)
                    )
                    .order_by(Payment.created_at.desc())
                )
                check_res = await db.execute(check_stmt)
                existing_payment = check_res.scalars().first()
                if existing_payment:
                    logger.info(
                        f"[PAYMENT_SERVICE] Reusing active pending payment order "
                        f"{existing_payment.gateway_order_id} for invoice {target_invoice.id}"
                    )
                    return {
                        "payment": existing_payment,
                        "client_secret": existing_payment.gateway_order_id,
                        "payment_intent_id": existing_payment.gateway_order_id,
                        "status": "created"
                    }

        # Canonical Server-Generated Metadata (do not trust arbitrary client metadata)
        canonical_metadata = {
            "user_id": user_id,
            "payment_type": payment_type_clean,
            "invoice_id": invoice_id,
            "subscription_id": subscription_id
        }
        if payment_metadata and isinstance(payment_metadata, dict):
            for safe_k in ["billing_cycle", "plan_code"]:
                if safe_k in payment_metadata and payment_metadata[safe_k] is not None:
                    canonical_metadata[safe_k] = str(payment_metadata[safe_k])

        # Validate currency can be converted to minor units
        _ = to_minor_units(amount, currency)

        # Call External Payment Gateway (Razorpay or Stripe)
        gateway_response = await payment_gateway_service.create_payment(
            provider_name=provider_clean,
            amount=amount,
            currency=currency,
            metadata=canonical_metadata
        )

        gw_order_id = gateway_response.get("payment_intent_id")
        payment_reference = f"PAY-{uuid.uuid4().hex[:12].upper()}"

        payment = Payment(
            user_id=user_id,
            invoice_id=invoice_id,
            subscription_id=subscription_id,
            provider=provider_clean,
            payment_type=payment_type_clean,
            payment_method=payment_method,
            amount=amount,
            currency=currency,
            status=PENDING,
            payment_reference=payment_reference,
            gateway_order_id=gw_order_id,
            payment_metadata=canonical_metadata
        )

        try:
            saved_payment = await payment_repository.create(
                db,
                payment
            )
        except Exception as db_err:
            logger.critical(
                f"[CRITICAL_PAYMENT_DB_PERSISTENCE_FAILED] Gateway order was created but DB persistence failed! "
                f"gateway_order_id={gw_order_id} provider={provider_clean} user_id={user_id} invoice_id={invoice_id} "
                f"error={db_err}"
            )
            raise HTTPException(status_code=500, detail="Failed to persist payment order")

        return {
            "payment": saved_payment,
            "client_secret": gateway_response["client_secret"],
            "payment_intent_id": gateway_response["payment_intent_id"],
            "status": gateway_response["status"]
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
    
    async def get_all_payments(
        self,
        db
    ):

        return await (
            payment_repository
            .get_all(
                db
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
        
        if payment.status == PAID:

            return payment

        payment.status = PAID

        payment.processed_at = (
            datetime.utcnow()
        )

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
        gateway_order_id: str,
        gateway_payment_id: str = None
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
        
        if payment.status == PAID:

            return payment

        payment.status = PAID

        payment.processed_at = (
            datetime.utcnow()
        )

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

    async def mark_failed(
        self,
        db,
        payment_id: int,
        reason: str = None
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

        if payment.status == PAID:

            return payment

        payment.status = FAILED

        payment.failure_reason = (
            reason
        )

        payment.processed_at = (
            datetime.utcnow()
        )

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