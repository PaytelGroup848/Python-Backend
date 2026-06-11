import json

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


@router.post("/razorpay")
async def razorpay_webhook(

    request: Request,

    db: AsyncSession = Depends(
        get_db
    ),

    x_razorpay_signature: str = Header(
        alias="X-Razorpay-Signature"
    )
):

    payload = await request.body()

    try:

        await (
            payment_gateway_service
            .verify_webhook(

                provider_name="razorpay",

                payload=payload,

                signature=
                    x_razorpay_signature
            )
        )

    except Exception as e:

        raise HTTPException(

            status_code=400,

            detail=str(e)
        )

    event = json.loads(
        payload.decode()
    )

    if event["event"] == (
        "payment.captured"
    ):

        payment_entity = (

            event["payload"]
            ["payment"]
            ["entity"]
        )

        order_id = (
            payment_entity["order_id"]
        )

        payment_id = (
            payment_entity["id"]
        )

        print(

            f"RAZORPAY_PAYMENT_SUCCESS "

            f"order={order_id} "

            f"payment={payment_id}"
        )

        payment = await (
            payment_service
            .mark_paid_by_gateway_id(

                db,

                order_id,

                payment_id
            )
        )

        if payment:

            if payment.invoice_id:

                await (
                    invoice_service
                    .mark_paid(

                        db=db,

                        invoice_id=
                            payment.invoice_id,

                        payment_provider=
                            payment.provider,

                        payment_reference=
                            payment_id
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

    elif event["event"] == (
        "payment.failed"
    ):

        payment_entity = (

            event["payload"]
            ["payment"]
            ["entity"]
        )

        order_id = (
            payment_entity["order_id"]
        )

        print(

            f"RAZORPAY_PAYMENT_FAILED "

            f"order={order_id}"
        )

        payment = await (
            payment_service
            .get_by_gateway_order_id(

                db,

                order_id

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

    elif event["event"] == (
        "refund.processed"
    ):

        refund_entity = (

            event["payload"]
            ["refund"]
            ["entity"]
        )

        payment_id = (
            refund_entity["payment_id"]
        )

        print(

            f"RAZORPAY_REFUND_PROCESSED "

            f"payment={payment_id}"
        )

        payment = await (
            payment_service
            .get_by_gateway_payment_id(

                db,

                payment_id
            )
        )

        if payment:

            await (
                payment_service
                .mark_refunded(

                    db,

                    payment.id
                )
            )

    return {

        "status":
            "success"
    }