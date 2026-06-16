from sqlalchemy import func
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.api_request import (
    ApiRequest
)

from app.modules.billing.models.subscription import (
    Subscription
)

from app.modules.billing.models.payment import (
    Payment
)


class AdminRepository:

    async def get_dashboard_metrics(
        self,
        db: AsyncSession,
    ):

        total_users_result = await db.execute(
            select(func.count(User.id))
        )

        active_users_result = await db.execute(
            select(func.count(User.id))
            .where(User.is_active == True)
        )

        active_subscriptions_result = await db.execute(
            select(func.count(Subscription.id))
            .where(
                Subscription.status == "active"
            )
        )

        total_requests_result = await db.execute(
            select(func.count(ApiRequest.id))
        )

        total_tokens_result = await db.execute(
            select(
                func.coalesce(
                    func.sum(
                        ApiRequest.total_tokens
                    ),
                    0
                )
            )
        )

        revenue_result = await db.execute(
            select(
                func.coalesce(
                    func.sum(
                        Payment.amount
                    ),
                    0
                )
            )
            .where(
                Payment.status == "paid"
            )
        )

        total_users = (
            total_users_result.scalar() or 0
        )

        active_users = (
            active_users_result.scalar() or 0
        )

        active_subscriptions = (
            active_subscriptions_result.scalar() or 0
        )

        total_requests = (
            total_requests_result.scalar() or 0
        )

        total_tokens = (
            total_tokens_result.scalar() or 0
        )

        monthly_revenue = float(
            revenue_result.scalar() or 0
        )

        return {

            "total_users":
                total_users,

            "active_users":
                active_users,

            "active_subscriptions":
                active_subscriptions,

            "total_requests":
                total_requests,

            "total_tokens":
                total_tokens,

            "monthly_revenue":
                monthly_revenue,

            "active_providers":
                5,

            "active_workers":
                4,
        }