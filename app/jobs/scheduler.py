from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler
)

from app.modules.billing.jobs.subscription_expiry_job import (
    process_expired_subscriptions
)


scheduler = AsyncIOScheduler()

scheduler.add_job(

    process_expired_subscriptions,

    trigger="cron",

    hour=0,

    minute=5
)