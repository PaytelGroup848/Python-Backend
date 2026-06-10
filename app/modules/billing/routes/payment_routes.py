from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.core.security import (
    verify_token
)

from app.modules.billing.services.payment_service import (
    payment_service
)

from app.modules.billing.schemas.payment_schema import (

    CreatePaymentRequest,

    PaymentResponse,

    PaymentListResponse,

    PaymentGatewayResponse
)

router = APIRouter(

    prefix="/payments",

    tags=["Payments"]
)

@router.post(
    "/create",
    response_model=PaymentGatewayResponse
)
async def create_payment(

    payload: CreatePaymentRequest,

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    payment = await (
        payment_service.create_payment(

            db=db,

            user_id=
                user["user_id"],

            provider=
                payload.provider,

            payment_type=
                payload.payment_type,

            amount=
                payload.amount,

            currency=
                payload.currency,

            invoice_id=
                payload.invoice_id,

            subscription_id=
                payload.subscription_id,

            payment_metadata=
                payload.payment_metadata
        )
    )

    return payment

@router.get(
    "/{payment_id}",
    response_model=PaymentResponse
)
async def get_payment(

    payment_id: int,

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    payment = await (
        payment_service.get_payment(

            db,

            payment_id
        )
    )

    if not payment:

        raise HTTPException(

            status_code=404,

            detail="Payment not found"
        )

    if payment.user_id != user["user_id"]:

        raise HTTPException(

            status_code=403,

            detail="Access denied"
        )

    return payment

@router.get(
    "/me/list",
    response_model=PaymentListResponse
)
async def my_payments(

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    payments = await (
        payment_service.get_user_payments(

            db,

            user["user_id"]
        )
    )

    return {

        "total":
            len(payments),

        "payments":
            payments
    }
