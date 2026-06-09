from app.modules.billing.repositories.usage_limit_repository import (
    usage_limit_repository
)

from app.modules.billing.repositories.subscription_repository import (
    subscription_repository
)

from app.modules.api_requests.repositories.api_request_repository import (
    ApiRequestRepository
)


class UsageLimitService:

    def __init__(self):

        self.api_request_repository = (
            ApiRequestRepository()
        )

    async def get_plan_limits(
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

        return await (
            usage_limit_repository
            .get_by_plan(
                db,
                subscription.plan_name
            )
        )

    async def check_token_limit(
        self,
        db,
        user_id: int
    ):

        limits = await (
            self.get_plan_limits(
                db,
                user_id
            )
        )

        if not limits:

            return False

        usage = await (
            self.api_request_repository
            .get_user_requests(
                db,
                user_id
            )
        )

        total_tokens = sum(

            row.total_tokens or 0

            for row in usage
        )

        return (

            total_tokens
            <
            limits.monthly_token_limit
        )

    async def check_request_limit(
        self,
        db,
        user_id: int
    ):

        limits = await (
            self.get_plan_limits(
                db,
                user_id
            )
        )

        if not limits:

            return False

        usage = await (
            self.api_request_repository
            .get_user_requests(
                db,
                user_id
            )
        )

        return (

            len(usage)
            <
            limits.monthly_request_limit
        )

    async def can_make_request(
        self,
        db,
        user_id: int
    ):

        token_ok = await (
            self.check_token_limit(
                db,
                user_id
            )
        )

        request_ok = await (
            self.check_request_limit(
                db,
                user_id
            )
        )

        return (
            token_ok
            and
            request_ok
        )


usage_limit_service = (
    UsageLimitService()
)