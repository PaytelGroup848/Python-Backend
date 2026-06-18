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

from app.modules.billing.services.invoice_service import (
    invoice_service
)

from app.modules.billing.services.subscription_service import (
    subscription_service
)

router = APIRouter(

    prefix="/webhooks",

    tags=["Webhooks"]
)

@router.post("/stripe")
async def stripe_webhook(

    request: Request,

    db: AsyncSession = Depends(
        get_db
    ),

    stripe_signature: str = Header(
        alias="Stripe-Signature"
    )
):
    payload = await request.body()

    try:

        event = await (
            payment_gateway_service
            .verify_webhook(

                provider_name="stripe",

                payload=payload,

                signature=stripe_signature
            )
        )

    except Exception as e:

        raise HTTPException(

            status_code=400,

            detail=str(e)
        )
    
    if event["type"] == (
        "payment_intent.succeeded"
    ):

        payment_intent = (
            event["data"]["object"]
        )

        payment_intent_id = (
            payment_intent["id"]
        )

        print(
            f"STRIPE_PAYMENT_SUCCESS="
            f"{payment_intent_id}"
        )

        payment = await (
            payment_service
            .mark_paid_by_gateway_id(
                db,
                payment_intent_id
            )
        )

        if payment:

            if payment.invoice_id:

                await (
                    invoice_service
                    .mark_paid(
                        db=db,
                        invoice_id=payment.invoice_id,
                        payment_provider=payment.provider,
                        payment_reference=payment.payment_reference,
                        external_reference=payment.gateway_payment_id
                    )
                )

            if payment.subscription_id:

                await (
                    subscription_service
                    .activate_subscription(
                        db,
                        payment.subscription_id
                    )
                )

    if event["type"] == (
        "payment_intent.payment_failed"
    ):

        payment_intent = (
            event["data"]["object"]
        )

        payment_intent_id = (
            payment_intent["id"]
        )

        print(
            f"STRIPE_PAYMENT_FAILED="
            f"{payment_intent_id}"
        )

        payment = await (
            payment_service
            .get_by_gateway_order_id(

                db,

                payment_intent_id
            )
        )

        if payment:

            await (
                payment_service
                .mark_failed(

                    db,

                    payment.id
                )
            )

        return {
            "status": "success"
        }

