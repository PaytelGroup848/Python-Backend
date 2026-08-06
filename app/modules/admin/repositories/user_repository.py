from sqlalchemy import (
    select,
    func
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.models.user import User

from app.models.api_request import (
    ApiRequest
)

from app.modules.billing.models.subscription import (
    Subscription
)

from app.modules.billing.models.plan_version import (
    PlanVersion
)


class UserRepository:

    async def get_users(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(

                User,

                Subscription.plan_name,

                PlanVersion.monthly_token_limit,

                func.coalesce(
                    func.sum(
                        ApiRequest.total_tokens
                    ),
                    0
                ).label(
                    "total_tokens"
                )
            )

            .outerjoin(
                Subscription,
                (
                    (Subscription.user_id == User.id)
                    &
                    (Subscription.status == "active")
                )
            )

            .outerjoin(
                PlanVersion,
                (
                    PlanVersion.id
                    ==
                    Subscription.plan_version_id
                )
            )

            .outerjoin(
                ApiRequest,
                User.id == ApiRequest.user_id
            )

            .group_by(
                User.id,
                Subscription.plan_name,
                PlanVersion.monthly_token_limit
            )
        )

        rows = result.all()

        users = []

        for (

            user,
            plan_name,
            monthly_token_limit,
            total_tokens
        ) in rows:

            raw_plan = str(plan_name or "free").lower()
            if "pro" in raw_plan:
                norm_plan = "pro"
            elif "enterprise" in raw_plan:
                norm_plan = "enterprise"
            else:
                norm_plan = "free"

            user.plan_name = norm_plan

            # Set correct monthly token limits and remaining tokens
            if monthly_token_limit and monthly_token_limit > 0:
                token_limit = monthly_token_limit
            elif norm_plan == "pro":
                token_limit = 50000000
            elif norm_plan == "enterprise":
                token_limit = 250000000
            else:
                token_limit = 10000000

            user.monthly_token_limit = token_limit
            user.total_tokens = total_tokens or 0
            user.remaining_tokens = max(0, token_limit - (total_tokens or 0))

            users.append(user)

        return users


    async def get_by_id(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()