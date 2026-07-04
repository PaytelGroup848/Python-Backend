from app.modules.billing.repositories.subscription_repository import (
    subscription_repository
)

from app.modules.billing.repositories.plan_repository import (
    plan_repository
)

from app.modules.usage.repositories.usage_repository import (
    usage_repository
)

from app.modules.billing.repositories.plan_version_repository import (
    plan_version_repository
)

from app.db.redis_client import (
    redis_client
)

from datetime import datetime


class UsageLimitService:

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
    
    async def get_user_plan_version(
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

            free_plan = await (
                plan_repository
                .get_by_code(
                    db,
                    "free"
                )
            )

            if not free_plan:

                return None

            return await (
                plan_version_repository
                .get_active_by_plan(
                    db,
                    free_plan.id
                )
            )

        if not subscription.plan_version_id:

            return None

        return await (
            plan_version_repository
            .get_by_id(
                db,
               subscription.plan_version_id
            )
        )

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

        limits = await (
            self.get_user_plan_version(
                db,
                user_id
            )
        )

        if not limits:

            return False

        if (
            subscription.end_date
            and
            subscription.end_date < datetime.utcnow()
        ):
            return False

        limits = await (
            self.get_user_plan_version(
                db,
                user_id
            )
        )

        if not limits:

            return False

        used_tokens = await (
            usage_repository
            .get_user_monthly_tokens(
                db,
                user_id
            )
        )

        total_requests = await (
            usage_repository
            .get_user_monthly_requests(
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
    
    async def get_user_limits(
        self,
        db,
        user_id: int
    ):

        version = await (
            self.get_user_plan_version(
                db,
                user_id
            )
        )

        return version
    
    async def get_usage_summary(
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

        limits = await (
            self.get_user_plan_version(
                db,
                user_id
            )
        )

        if not limits:

            return {

                "plan": "free",

                "used_tokens": 0,

                "remaining_tokens": 0,

                "used_requests": 0,

                "remaining_requests": 0,

                "monthly_token_limit": 0,

                "monthly_request_limit": 0,

                "monthly_cost_limit": 0
            }

        plan = (
            subscription.plan_name
            if subscription
            else "free"
        )

        used_tokens = await (
            usage_repository
            .get_user_monthly_tokens(
                db,
                user_id
            )
        )

        used_requests = await (
            usage_repository
            .get_user_monthly_requests(
                db,
                user_id
            )
        )

        return {

            "plan":
                plan,

            "used_tokens":
                used_tokens,

            "remaining_tokens":
                max(
                    0,
                    limits.monthly_token_limit
                    - used_tokens
                ),

            "used_requests":
                used_requests,

            "remaining_requests":
                max(
                    0,
                    limits.monthly_request_limit
                    - used_requests
                ),

            "monthly_token_limit":
                limits.monthly_token_limit,

            "monthly_request_limit":
                limits.monthly_request_limit,

            "monthly_cost_limit":
                limits.monthly_cost_limit
        }
    
usage_limit_service = (
    UsageLimitService()
)