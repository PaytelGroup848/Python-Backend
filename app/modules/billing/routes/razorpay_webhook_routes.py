import json
import logging
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.modules.billing.services.payment_gateway_service import payment_gateway_service
from app.modules.billing.services.payment_service import payment_service
from app.modules.billing.services.billing_payment_processor import billing_payment_processor

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_razorpay_signature: str = Header(alias="X-Razorpay-Signature")
):
    payload = await request.body()

    try:
        await payment_gateway_service.verify_webhook(
            provider_name="razorpay",
            payload=payload,
            signature=x_razorpay_signature
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    event = json.loads(payload.decode())
    event_type = event.get("event")

    if event_type == "payment.captured":
        payment_entity = event["payload"]["payment"]["entity"]
        order_id = payment_entity["order_id"]
        payment_id = payment_entity["id"]

        logger.info(f"RAZORPAY_PAYMENT_SUCCESS order={order_id} payment={payment_id}")

        try:
            await billing_payment_processor.process_successful_payment(
                db=db,
                gateway_order_id=order_id,
                gateway_payment_id=payment_id
            )
        except Exception as e:
            logger.error(f"RAZORPAY_WEBHOOK_PROCESSING_ERROR order={order_id}: {e}")

    elif event_type == "payment.failed":
        payment_entity = event["payload"]["payment"]["entity"]
        order_id = payment_entity["order_id"]

        logger.info(f"RAZORPAY_PAYMENT_FAILED order={order_id}")

        payment = await payment_service.get_by_gateway_order_id(db, order_id)
        if payment:
            await payment_service.mark_failed(db, payment.id)

    elif event_type == "refund.processed":
        refund_entity = event["payload"]["refund"]["entity"]
        payment_id = refund_entity["payment_id"]

        logger.info(f"RAZORPAY_REFUND_PROCESSED payment={payment_id}")

        payment = await payment_service.get_by_gateway_payment_id(db, payment_id)
        if payment:
            await payment_service.mark_refunded(db, payment.id)

    return {
        "status": "success"
    }