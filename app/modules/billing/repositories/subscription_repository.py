from sqlalchemy import select

from datetime import datetime

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

        try:

            db.add(
                subscription
            )

            await db.commit()

            await db.refresh(
                subscription
            )

            return subscription

        except Exception:

            await db.rollback()

            raise

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
    
    async def get_by_id(
        self,
        db: AsyncSession,
        subscription_id: int
    ):

        result = await db.execute(

            select(Subscription)

        .   where(
                Subscription.id
                == subscription_id
            )
        )

        return(
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

        try:

            await db.commit()

            await db.refresh(
                subscription
            )

            return subscription

        except Exception:

            await db.rollback()

            raise

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

            .where(
                Subscription.end_date
                < datetime.utcnow()
            )
        )

        return (
            result.scalars()
            .all()
        )


subscription_repository = (
    SubscriptionRepository()
)