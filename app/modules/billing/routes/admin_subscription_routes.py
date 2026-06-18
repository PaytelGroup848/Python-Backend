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
    require_role
)

from app.modules.billing.repositories.subscription_repository import (
    subscription_repository
)

from app.modules.billing.services.subscription_service import (
    subscription_service
)

router = APIRouter(

    prefix="/admin/subscriptions",

    tags=["Admin Subscriptions"]
)

@router.get("")
async def get_subscriptions(

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    subscriptions = await (
        subscription_repository
        .get_all(db)
    )

    return {

        "count":
            len(subscriptions),

        "subscriptions": [

            {
                "id":
                    subscription.id,

                "user_id":
                    subscription.user_id,

                "plan_id":
                    subscription.plan_id,

                "plan_name":
                    subscription.plan_name,

                "status":
                    subscription.status,

                "monthly_token_limit":
                    subscription.monthly_token_limit,

                "auto_renew":
                    subscription.auto_renew,

                "start_date":
                    subscription.start_date,

                "end_date":
                    subscription.end_date
            }

            for subscription
            in subscriptions
        ]
    }

@router.patch(
    "/{subscription_id}/activate"
)
async def activate_subscription(

    subscription_id: int,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    subscription = await (
        subscription_service
        .activate_subscription(
            db,
            subscription_id
        )
    )

    if not subscription:

        raise HTTPException(

            status_code=404,

            detail=
                "Subscription not found"
        )

    return {
        "message":
            "Subscription activated"
    }

@router.patch(
    "/{subscription_id}/cancel"
)
async def cancel_subscription(

    subscription_id: int,

    user=Depends(
        require_role("admin")
    ),

    db: AsyncSession = Depends(
        get_db
    )
):

    subscription = await (
        subscription_service
        .cancel_subscription_by_id(
            db,
            subscription_id
        )
    )

    if not subscription:

        raise HTTPException(

            status_code=404,

            detail=
                "Subscription not found"
        )

    return {
        "message":
            "Subscription cancelled"
    }
