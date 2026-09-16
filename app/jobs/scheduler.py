from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler
)

from app.modules.billing.jobs.subscription_expiry_job import (
    process_expired_subscriptions
)
from app.jobs.session_cleanup_job import (
    cleanup_expired_sessions
)


scheduler = AsyncIOScheduler()

scheduler.add_job(
    process_expired_subscriptions,
    trigger="cron",
    hour=0,
    minute=5
)

scheduler.add_job(
    cleanup_expired_sessions,
    trigger="cron",
    hour=3,
    minute=0
)