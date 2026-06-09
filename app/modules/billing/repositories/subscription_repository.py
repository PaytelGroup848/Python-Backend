from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.billing.models.subscription import (
    Subscription
)


class SubscriptionRepository:

    async def create(
        self,
        db: AsyncSession,
        subscription: Subscription
    ):

        db.add(subscription)

        await db.commit()

        await db.refresh(
            subscription
        )

        return subscription

    async def get_user_subscription(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(Subscription)

            .where(
                Subscription.user_id
                == user_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_active_subscription(
        self,
        db: AsyncSession,
        user_id: int
    ):

        result = await db.execute(

            select(Subscription)

            .where(
                Subscription.user_id
                == user_id
            )

            .where(
                Subscription.status
                == "active"
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def get_all(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(Subscription)
        )

        return (
            result.scalars()
            .all()
        )

    async def update(
        self,
        db: AsyncSession,
        subscription: Subscription
    ):

        await db.commit()

        await db.refresh(
            subscription
        )

        return subscription

    async def delete(
        self,
        db: AsyncSession,
        subscription: Subscription
    ):

        await db.delete(
            subscription
        )

        await db.commit()

    async def get_expired_subscriptions(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(Subscription)

            .where(
                Subscription.status
                == "active"
            )

            .where(
                Subscription.end_date
                != None
            )
        )

        return (
            result.scalars()
            .all()
        )


subscription_repository = (
    SubscriptionRepository()
)