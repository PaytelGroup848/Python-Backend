import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter

from app.db.database import get_db
from app.core.security import verify_token
from app.core.config import settings
from app.modules.billing.services.subscription_checkout_service import subscription_checkout_service
from app.modules.billing.services.plan_service import plan_service
from app.modules.billing.services.billing_payment_processor import billing_payment_processor
from app.modules.billing.schemas.subscription_schema import (
    SubscriptionPurchaseRequest,
    VerifyPaymentRequest,
)

limiter = Limiter(
    key_func=lambda request: request.headers.get("authorization", "anonymous")
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
)


@router.post("/purchase")
@limiter.limit("5/minute")
async def purchase_subscription(
    request: Request,
    payload: SubscriptionPurchaseRequest,
    user=Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    try:
        checkout_plan = await plan_service.get_checkout_plan(
            db=db,
            plan_code=payload.plan_code,
            provider=payload.provider,
            billing_cycle=payload.billing_cycle,
            currency=payload.currency
        )

        metadata = payload.payment_metadata or {}
        metadata.update({
            "billing_cycle": payload.billing_cycle,
            "plan_code": payload.plan_code
        })

        result = await subscription_checkout_service.create_subscription_checkout(
            db=db,
            user_id=user["user_id"],
            plan_id=checkout_plan["plan"].id,
            plan_version_id=checkout_plan["version"].id,
            amount=checkout_plan["price"].amount,
            currency=checkout_plan["price"].currency,
            provider=checkout_plan["price"].provider,
            auto_renew=payload.auto_renew,
            payment_metadata=metadata
        )

        razorpay_key_id = (
            settings.RAZORPAY_KEY_ID
            if payload.provider.lower() == "razorpay"
            else None
        )

        return {
            **result,
            "razorpay_key_id": razorpay_key_id
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/verify-payment")
async def verify_subscription_payment(
    payload: VerifyPaymentRequest,
    user=Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Synchronous cryptographic and server-side payment verification.
    1. Validates HMAC-SHA256 signature using RAZORPAY_KEY_SECRET.
    2. Derives payment, verifies user ownership & order amount.
    3. Executes atomic idempotent settlement via billing_payment_processor.
    """
    if not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Payment provider secret not configured on server"
        )

    expected_msg = f"{payload.razorpay_order_id}|{payload.razorpay_payment_id}".encode()
    generated_signature = hmac.new(
        key=settings.RAZORPAY_KEY_SECRET.encode(),
        msg=expected_msg,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, payload.razorpay_signature):
        raise HTTPException(
            status_code=400,
            detail="Invalid cryptographic payment signature"
        )

    try:
        settlement = await billing_payment_processor.process_successful_payment(
            db=db,
            gateway_order_id=payload.razorpay_order_id,
            gateway_payment_id=payload.razorpay_payment_id,
            expected_user_id=user["user_id"],
            expected_provider="razorpay"
        )

        return {
            "status": "verified",
            "subscription": "active",
            "payment_id": settlement.get("payment_id"),
            "subscription_id": settlement.get("subscription_id"),
            "message": settlement.get("message", "Subscription activated successfully")
        }

    except PermissionError as pe:
        raise HTTPException(
            status_code=403,
            detail=str(pe)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Payment settlement error: {str(e)}"
        )