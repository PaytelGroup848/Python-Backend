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

from app.modules.billing.services.plan_service import (
    plan_service
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
        plan_id: int,
        plan_version_id: int,
        auto_renew: bool = False
    ):

        plan = await (
            plan_service
            .get_by_id(
                db,
                plan_id
            )
        )

        if not plan:

            raise ValueError(
                "Plan not found"
            )

        version = await (
            plan_service
            .get_version_by_id(
                db,
                plan_version_id
            )
        )

        if not version:

            raise ValueError(
                "Plan version not found"
            )

        subscription = Subscription(

            user_id=user_id,

            plan_id=plan_id,

            plan_version_id=
                plan_version_id,

            plan_name=
                plan.plan_code,

            monthly_token_limit=
                version.monthly_token_limit,

            status="pending",

            auto_renew=
                auto_renew,

            start_date=None,

            end_date=None
        )

        return await (
            subscription_repository
            .create(
                db,
                subscription
            )
        )
    
    async def activate_subscription(
        self,
        db,
        subscription_id: int
    ):

        subscription = await (
            subscription_repository.get_by_id(
                db,
                subscription_id
            )
        )

        if not subscription:
            return None

        subscription.status = "active"

        subscription.start_date = (
            datetime.utcnow()
        )

        subscription.end_date = (
            datetime.utcnow()
            + timedelta(days=30)
        )

        return await (
            subscription_repository.update(
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
    
    async def change_user_plan(
        self,
        db,
        user_id: int,
        plan_name: str
    ):

        subscription = await (
            subscription_repository
            .get_active_subscription(
                db,
                user_id
            )
        )

        if not subscription:

            raise ValueError(
                "Active subscription not found"
            )

        plan = await (
            plan_service
            .get_by_plan_code(
                db,
                plan_name
            )
        )

        if not plan:

            raise ValueError(
                f"Plan '{plan_name}' not found"
            )

        version = await (
            plan_service
            .get_active_version(
                db,
                plan.id
            )
        )

        if not version:

            raise ValueError(
                "Active plan version not found"
            )

        subscription.plan_id = (
            plan.id
        )

        subscription.plan_version_id = (
            version.id
        )

        subscription.plan_name = (
            plan.plan_code
        )

        subscription.monthly_token_limit = (
            version.monthly_token_limit
        )

        return await (
            subscription_repository
            .update(
                db,
                subscription
            )
        )


subscription_service = (
    SubscriptionService()
)