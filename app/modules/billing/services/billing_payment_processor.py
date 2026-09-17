import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.modules.billing.models.payment import Payment
from app.modules.billing.models.invoice import Invoice
from app.modules.billing.models.subscription import Subscription
from app.modules.billing.models.wallet_transaction import WalletTransaction
from app.modules.billing.constants.payment_status import PENDING, PAID
from app.modules.billing.services.wallet_service import wallet_service
from app.modules.billing.utils.money import to_minor_units
from app.shared.redis.client import redis_client

logger = logging.getLogger(__name__)


class BillingPaymentProcessor:
    """
    Unified, idempotent, concurrency-safe payment settlement engine.
    Used by client verify-payment API, Razorpay webhook, and Stripe webhook.

    Guarantees:
    1. Row-level locking (SELECT FOR UPDATE) on Payment prevents simultaneous processing.
    2. Explicit logical execution ordering: identity/ownership validated before idempotent short-circuit.
    3. Exact minor-unit integer equality (zero float tolerance).
    4. Immutable invoice settlement strictly using payment.invoice_id.
    5. User-level row lock serializes multi-subscription activations for the same user.
    6. Double-crediting protection on wallet transactions.
    7. Post-commit, non-blocking Redis cache invalidation.
    """

    async def process_successful_payment(
        self,
        db: AsyncSession,
        gateway_order_id: str,
        gateway_payment_id: Optional[str] = None,
        expected_user_id: Optional[int] = None,
        expected_provider: Optional[str] = None,
        gateway_amount_minor: Optional[int] = None,
        gateway_currency: Optional[str] = None
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

        # 2. Identity, Provider Correlation, & Ownership Validation
        if expected_provider is not None and payment.provider.lower() != expected_provider.lower():
            raise ValueError(
                f"Provider mismatch: payment was created for '{payment.provider}', but received webhook for '{expected_provider}'"
            )

        if expected_user_id is not None and payment.user_id != expected_user_id:
            raise PermissionError(f"Payment order {gateway_order_id} does not belong to user {expected_user_id}")

        # 3. Idempotent Check: If already PAID, return success immediately (safe because ownership already verified)
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
            raise ValueError(
                f"Invalid payment state transition from '{payment.status}' to '{PAID}' for order {gateway_order_id}"
            )

        # 5. Exact Currency and Minor-Unit Integer Comparison (Zero Tolerance)
        if gateway_currency is not None and payment.currency.upper() != gateway_currency.upper():
            raise ValueError(f"Currency mismatch: recorded '{payment.currency}', received '{gateway_currency}'")

        if gateway_amount_minor is not None:
            db_minor = to_minor_units(payment.amount, payment.currency)
            if db_minor != gateway_amount_minor:
                raise ValueError(
                    f"Exact amount mismatch: DB requires {db_minor} minor units, gateway reported {gateway_amount_minor}"
                )

        now = datetime.utcnow()

        # 6. Settle Invoice strictly by payment.invoice_id (Never re-resolve dynamically)
        if payment.invoice_id:
            inv_stmt = (
                select(Invoice)
                .where(Invoice.id == payment.invoice_id)
                .with_for_update()
            )
            inv_res = await db.execute(inv_stmt)
            invoice = inv_res.scalar_one_or_none()

            if not invoice:
                raise ValueError(f"Associated invoice {payment.invoice_id} not found")

            # Cross-verify invoice amount against gateway reported minor units
            if gateway_amount_minor is not None:
                inv_minor = to_minor_units(invoice.amount, invoice.currency)
                if inv_minor != gateway_amount_minor:
                    raise ValueError(
                        f"Exact invoice amount mismatch: invoice requires {inv_minor} minor units, gateway reported {gateway_amount_minor}"
                    )

            invoice.status = "paid"
            invoice.paid_at = now
            invoice.payment_provider = payment.provider
            invoice.payment_reference = gateway_payment_id or payment.payment_reference

        # 7. Settle Wallet Recharge with Double-Crediting Protection
        if payment.payment_type == "wallet":
            # Check if a completed WalletTransaction already exists for this payment reference
            tx_stmt = (
                select(WalletTransaction)
                .where(
                    WalletTransaction.reference_type == "payment",
                    WalletTransaction.reference_id == payment.payment_reference
                )
            )
            tx_res = await db.execute(tx_stmt)
            existing_tx = tx_res.scalar_one_or_none()

            if not existing_tx:
                await wallet_service.credit_wallet(
                    db=db,
                    user_id=payment.user_id,
                    amount=payment.amount,
                    description=f"Online wallet recharge via {payment.provider.title()}",
                    reference_type="payment",
                    reference_id=payment.payment_reference
                )
                logger.info(
                    f"[PAYMENT_PROCESSOR] Credited wallet for user {payment.user_id} with {payment.amount} {payment.currency}"
                )
            else:
                logger.info(
                    f"[PAYMENT_PROCESSOR] Wallet transaction for reference {payment.payment_reference} already exists. Skipping duplicate credit."
                )

        # 8. Settle Subscription Activation with User-Level Concurrency Row Lock
        if payment.subscription_id:
            # Lock User row to strictly serialize concurrent multi-subscription settlements for the same user
            user_stmt = select(User).where(User.id == payment.user_id).with_for_update()
            await db.execute(user_stmt)

            duration_days = 30
            if payment.payment_metadata and isinstance(payment.payment_metadata, dict):
                cycle = payment.payment_metadata.get("billing_cycle", "monthly")
                if cycle == "yearly":
                    duration_days = 365

            # Atomically supersede and cancel previous active subscriptions for this user
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
                logger.info(
                    f"[PAYMENT_PROCESSOR] Superseded previous active subscription {prev_sub.id} for user {payment.user_id}"
                )

            # Activate target subscription
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
                logger.info(
                    f"[PAYMENT_PROCESSOR] Activated subscription {subscription.id} ({subscription.plan_name}) until {subscription.end_date}"
                )

        # 9. Transition Payment to PAID
        payment.status = PAID
        payment.processed_at = now
        if gateway_payment_id:
            payment.gateway_payment_id = gateway_payment_id

        # 10. Atomic DB Commit
        await db.commit()
        await db.refresh(payment)

        # 11. POST-COMMIT CACHE INVALIDATION (Non-blocking, isolated from financial transaction)
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
            "message": "Payment verified and settled successfully"
        }


billing_payment_processor = BillingPaymentProcessor()


