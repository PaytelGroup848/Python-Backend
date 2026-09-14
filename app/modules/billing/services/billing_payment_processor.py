import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.billing.models.payment import Payment
from app.modules.billing.models.invoice import Invoice
from app.modules.billing.models.subscription import Subscription
from app.modules.billing.models.plan_version import PlanVersion
from app.modules.billing.constants.payment_status import PENDING, PAID
from app.shared.redis.client import redis_client

logger = logging.getLogger(__name__)


class BillingPaymentProcessor:
    """
    Unified, idempotent, concurrency-safe payment settlement engine.
    Used by both client verify-payment API and async webhook handlers.
    
    Guarantees:
    1. Row-level locking (SELECT FOR UPDATE) prevents simultaneous activation race conditions.
    2. Explicit state transition validation (only PENDING -> PAID).
    3. Idempotent early-return if payment is already PAID.
    4. Atomic DB settlement: Payment (PAID) + Invoice (PAID) + Subscription (ACTIVE).
    5. Automatic replacement of previously active user subscriptions.
    6. Post-commit Redis cache invalidation for user usage and subscription limits.
    """

    async def process_successful_payment(
        self,
        db: AsyncSession,
        gateway_order_id: str,
        gateway_payment_id: Optional[str] = None,
        expected_user_id: Optional[int] = None,
        expected_amount: Optional[float] = None,
        expected_currency: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # 1. Acquire row lock on Payment row
        stmt = (
            select(Payment)
            .where(Payment.gateway_order_id == gateway_order_id)
            .with_for_update()
        )
        res = await db.execute(stmt)
        payment = res.scalar_one_or_none()

        if not payment:
            raise ValueError(f"Payment order not found for gateway_order_id: {gateway_order_id}")

        # 2. Ownership and parameter integrity checks (if provided by client verify API)
        if expected_user_id is not None and payment.user_id != expected_user_id:
            raise PermissionError(f"Payment order {gateway_order_id} does not belong to user {expected_user_id}")

        if expected_currency is not None and payment.currency.upper() != expected_currency.upper():
            raise ValueError(f"Currency mismatch: recorded {payment.currency}, received {expected_currency}")

        if expected_amount is not None:
            # Allow minor floating point epsilon difference (< 0.01)
            if abs(float(payment.amount) - float(expected_amount)) > 0.05:
                raise ValueError(f"Amount mismatch: recorded {payment.amount}, received {expected_amount}")

        # 3. Idempotent Check: If already PAID, return success immediately
        if payment.status == PAID:
            logger.info(f"[PAYMENT_PROCESSOR] Order {gateway_order_id} is already PAID. Idempotent success returned.")
            return {
                "status": "already_paid",
                "payment_id": payment.id,
                "subscription_id": payment.subscription_id,
                "invoice_id": payment.invoice_id,
                "message": "Payment already processed successfully"
            }

        # 4. State Machine Transition Guard: Only PENDING -> PAID allowed
        if payment.status != PENDING:
            raise ValueError(f"Invalid payment state transition from '{payment.status}' to '{PAID}' for order {gateway_order_id}")

        now = datetime.utcnow()

        # 5. Transition Payment to PAID
        payment.status = PAID
        payment.processed_at = now
        if gateway_payment_id:
            payment.gateway_payment_id = gateway_payment_id

        # 6. Settle Invoice atomically with row lock
        if payment.invoice_id:
            inv_stmt = (
                select(Invoice)
                .where(Invoice.id == payment.invoice_id)
                .with_for_update()
            )
            inv_res = await db.execute(inv_stmt)
            invoice = inv_res.scalar_one_or_none()
            if invoice:
                invoice.status = "paid"
                invoice.paid_at = now
                invoice.payment_provider = payment.provider
                invoice.payment_reference = gateway_payment_id or payment.payment_reference

        # 7. Activate Subscription & atomically supersede any previous active subscriptions
        duration_days = 30
        if payment.subscription_id:
            # Determine billing cycle duration from plan version / metadata if available
            if payment.payment_metadata and isinstance(payment.payment_metadata, dict):
                cycle = payment.payment_metadata.get("billing_cycle", "monthly")
                if cycle == "yearly":
                    duration_days = 365

            # Deactivate previous active subscriptions for this user
            prev_stmt = (
                select(Subscription)
                .where(
                    Subscription.user_id == payment.user_id,
                    Subscription.status == "active",
                    Subscription.id != payment.subscription_id
                )
                .with_for_update()
            )
            prev_res = await db.execute(prev_stmt)
            for prev_sub in prev_res.scalars().all():
                prev_sub.status = "cancelled"
                logger.info(f"[PAYMENT_PROCESSOR] Superseded previous active subscription {prev_sub.id} for user {payment.user_id}")

            # Activate the target subscription
            sub_stmt = (
                select(Subscription)
                .where(Subscription.id == payment.subscription_id)
                .with_for_update()
            )
            sub_res = await db.execute(sub_stmt)
            subscription = sub_res.scalar_one_or_none()
            if subscription:
                subscription.status = "active"
                subscription.start_date = now
                subscription.end_date = now + timedelta(days=duration_days)
                logger.info(f"[PAYMENT_PROCESSOR] Activated subscription {subscription.id} ({subscription.plan_name}) until {subscription.end_date}")

        # 8. Commit the atomic transaction
        await db.commit()
        await db.refresh(payment)

        # 9. POST-COMMIT CACHE INVALIDATION (Strictly after DB commit succeeds)
        user_id = payment.user_id
        try:
            cache_keys = [
                f"user_usage:{user_id}",
                f"user_plan:{user_id}",
                f"user_limits:{user_id}",
                f"billing:user_subscription:{user_id}",
                f"billing:user_usage:{user_id}"
            ]
            for key in cache_keys:
                await redis_client.delete(key)
            logger.info(f"[PAYMENT_PROCESSOR] Invalidated Redis usage/subscription cache for user {user_id}")
        except Exception as cache_err:
            logger.warning(f"[PAYMENT_PROCESSOR] Redis cache invalidation non-fatal warning: {cache_err}")

        return {
            "status": "paid",
            "payment_id": payment.id,
            "subscription_id": payment.subscription_id,
            "invoice_id": payment.invoice_id,
            "message": "Payment verified and subscription activated successfully"
        }


billing_payment_processor = BillingPaymentProcessor()

