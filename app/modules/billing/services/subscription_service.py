from datetime import (
    datetime,
    timedelta
)

from app.modules.billing.models.subscription import (
    Subscription
)

from app.modules.billing.repositories.subscription_repository import (
    subscription_repository
)


class SubscriptionService:

    async def get_user_subscription(
        self,
        db,
        user_id: int
    ):

        return await (
            subscription_repository
            .get_user_subscription(
                db,
                user_id
            )
        )

    async def get_active_subscription(
        self,
        db,
        user_id: int
    ):

        return await (
            subscription_repository
            .get_active_subscription(
                db,
                user_id
            )
        )

    async def create_subscription(
        self,
        db,
        user_id: int,
        plan_name: str,
        monthly_token_limit: int,
        auto_renew: bool = False
    ):

        subscription = Subscription(

            user_id=user_id,

            plan_name=plan_name,

            status="active",

            monthly_token_limit=
                monthly_token_limit,

            auto_renew=
                auto_renew,

            start_date=
                datetime.utcnow(),

            end_date=
                datetime.utcnow()
                + timedelta(days=30)
        )

        return await (
            subscription_repository
            .create(
                db,
                subscription
            )
        )

    async def cancel_subscription(
        self,
        db,
        user_id: int
    ):

        subscription = await (
            subscription_repository
            .get_active_subscription(
                db,
                user_id
            )
        )

        if not subscription:

            return False

        subscription.status = (
            "cancelled"
        )

        await (
            subscription_repository
            .update(
                db,
                subscription
            )
        )

        return True

    async def renew_subscription(
        self,
        db,
        user_id: int
    ):

        subscription = await (
            subscription_repository
            .get_active_subscription(
                db,
                user_id
            )
        )

        if not subscription:

            return None

        subscription.end_date = (
            datetime.utcnow()
            + timedelta(days=30)
        )

        return await (
            subscription_repository
            .update(
                db,
                subscription
            )
        )

    async def is_subscription_active(
        self,
        db,
        user_id: int
    ):

        subscription = await (
            subscription_repository
            .get_active_subscription(
                db,
                user_id
            )
        )

        if not subscription:

            return False

        if (
            subscription.end_date
            and
            subscription.end_date
            < datetime.utcnow()
        ):

            return False

        return True


subscription_service = (
    SubscriptionService()
)