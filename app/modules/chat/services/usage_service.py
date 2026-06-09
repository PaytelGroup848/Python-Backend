from app.modules.billing.repositories.subscription_repository import (
    subscription_repository
)

from app.modules.billing.repositories.usage_limit_repository import (
    usage_limit_repository
)

from app.modules.usage.repositories.usage_repository import (
    usage_repository
)

from app.db.redis_client import (
    redis_client
)


class UsageService:

    async def track_usage(
        self,
        user_id: int,
        tokens: int
    ):

        key = f"usage:{user_id}"

        current = await redis_client.get(
            key
        )

        current = (
            int(current)
            if current
            else 0
        )

        current += tokens

        await redis_client.setex(
            key,
            86400,
            current
        )

    async def get_user_plan(
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

            return "free"

        return subscription.plan_name

    async def check_usage_limit(
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

        limits = await (
            usage_limit_repository
            .get_by_plan(
                db,
                subscription.plan_name
            )
        )

        if not limits:

            return False

        used_tokens = await (
            usage_repository
            .get_user_total_tokens(
                db,
                user_id
            )
        )

        total_requests = await (
            usage_repository
            .get_user_total_requests(
                db,
                user_id
            )
        )

        if (
            used_tokens
            >= limits.monthly_token_limit
        ):

            return False

        if (
            total_requests
            >= limits.monthly_request_limit
        ):

            return False

        return True


usage_service = (
    UsageService()
)