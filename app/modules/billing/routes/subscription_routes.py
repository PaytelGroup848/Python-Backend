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

from app.modules.billing.services.subscription_checkout_service import (
    subscription_checkout_service
)

from app.modules.billing.services.plan_service import (
    plan_service
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

    try:

        checkout_plan = await (
            plan_service
            .get_checkout_plan(

                db=db,

                plan_code=
                    payload.plan_code,

                provider=
                    payload.provider,

                billing_cycle=
                    payload.billing_cycle,

                currency=
                    payload.currency
            )
        )

        result = await (
            subscription_checkout_service
            .create_subscription_checkout(

                db=db,

                user_id=
                    user["user_id"],

                plan_id=
                    checkout_plan["plan"].id,

                plan_version_id=
                    checkout_plan["version"].id,

                amount=
                    checkout_plan["price"].amount,

                currency=
                    checkout_plan["price"].currency,

                provider=
                    checkout_plan["price"].provider,

                auto_renew=
                    payload.auto_renew,

                payment_metadata=
                    payload.payment_metadata
            )
        )

        return result

    except ValueError as e:

        raise HTTPException(

            status_code=400,

            detail=str(e)
        )