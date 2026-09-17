import logging
from fastapi import (
    APIRouter,
    Request,
    Header,
    HTTPException,
    Depends
)
from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)
from app.modules.billing.services.payment_gateway_service import (
    payment_gateway_service
)
from app.modules.billing.services.payment_service import (
    payment_service
)
from app.modules.billing.services.billing_payment_processor import (
    billing_payment_processor
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: str = Header(alias="Stripe-Signature")
):
    payload = await request.body()

    try:
        event = await payment_gateway_service.verify_webhook(
            provider_name="stripe",
            payload=payload,
            signature=stripe_signature
        )
    except Exception as e:
        logger.warning(f"STRIPE_WEBHOOK_SIGNATURE_VERIFICATION_FAILED: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    event_type = event.get("type")

    if event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]
        gateway_amount_minor = int(payment_intent.get("amount", 0))
        gateway_currency = payment_intent.get("currency")

        logger.info(
            f"STRIPE_PAYMENT_SUCCESS id={payment_intent_id} "
            f"minor_amount={gateway_amount_minor} currency={gateway_currency}"
        )

        try:
            await billing_payment_processor.process_successful_payment(
                db=db,
                gateway_order_id=payment_intent_id,
                gateway_payment_id=payment_intent_id,
                expected_provider="stripe",
                gateway_amount_minor=gateway_amount_minor,
                gateway_currency=gateway_currency
            )
        except (ValueError, PermissionError) as ve:
            logger.warning(f"STRIPE_WEBHOOK_VALIDATION_REJECTED id={payment_intent_id}: {ve}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"STRIPE_WEBHOOK_PROCESSING_ERROR id={payment_intent_id}: {e}")
            raise HTTPException(status_code=500, detail="Webhook settlement error")

    elif event_type == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        logger.info(f"STRIPE_PAYMENT_FAILED id={payment_intent_id}")

        payment = await payment_service.get_by_gateway_order_id(
            db,
            payment_intent_id
        )
        if payment:
            await payment_service.mark_failed(
                db,
                payment.id,
                reason="Stripe payment intent failed"
            )

    return {
        "status": "success"
    }

