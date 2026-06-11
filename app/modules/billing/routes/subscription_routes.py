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
    verify_token
)

from app.modules.billing.services.subscription_checkout_service import (
    subscription_checkout_service
)

from app.modules.billing.schemas.subscription_schema import (
    SubscriptionPurchaseRequest
)


router = APIRouter(

    prefix="/subscriptions",

    tags=["Subscriptions"]
)


@router.post("/purchase")
async def purchase_subscription(

    payload: SubscriptionPurchaseRequest,

    user=Depends(
        verify_token
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    result = await (
        subscription_checkout_service
        .create_subscription_checkout(

            db=db,

            user_id=
                user["user_id"],

            plan_name=
                payload.plan_name,

            monthly_token_limit=
                payload.monthly_token_limit,

            amount=
                payload.amount,

            currency=
                payload.currency,

            provider=
                payload.provider,

            auto_renew=
                payload.auto_renew,

            payment_metadata=
                payload.payment_metadata
        )
    )

    return result