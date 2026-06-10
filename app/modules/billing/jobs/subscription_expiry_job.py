from datetime import datetime

from app.db.database import (
    AsyncSessionLocal
)

from app.modules.billing.repositories.subscription_repository import (
    subscription_repository
)


async def process_expired_subscriptions():

    async with AsyncSessionLocal() as db:

        subscriptions = await (
            subscription_repository
            .get_expired_subscriptions(
                db
            )
        )

        now = datetime.utcnow()

        expired_count = 0

        for subscription in subscriptions:

            if (
                subscription.end_date
                and
                subscription.end_date < now
            ):

                subscription.status = (
                    "expired"
                )

                await (
                    subscription_repository
                    .update(
                        db,
                        subscription
                    )
                )

                expired_count += 1

        return expired_count