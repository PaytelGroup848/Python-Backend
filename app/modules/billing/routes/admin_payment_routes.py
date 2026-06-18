from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.db.database import (
    get_db
)

from app.core.security import (
    require_role
)

from app.modules.billing.services.payment_service import (
    payment_service
)

router = APIRouter(

    prefix="/admin/payments",

    tags=["Admin Payments"]
)

@router.get("")
async def get_payments(

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    payments = await (
        payment_service
        .get_all_payments(
            db
        )
    )

    return {

        "count":
            len(payments),

        "payments": [

            {
                "id":
                    payment.id,

                "payment_reference":
                    payment.payment_reference,

                "user_id":
                    payment.user_id,

                "provider":
                    payment.provider,

                "payment_type":
                    payment.payment_type,

                "amount":
                    float(payment.amount),

                "currency":
                    payment.currency,

                "status":
                    payment.status,

                "created_at":
                    payment.created_at
            }

            for payment
            in payments
        ]
    }