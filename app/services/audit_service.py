from app.db.database import AsyncSessionLocal
from app.models.audit import AuditLog


async def log_action(
    user_id: int,
    action: str,
    endpoint: str
):

    async with AsyncSessionLocal() as db:

        log = AuditLog(
            user_id=user_id,
            action=action,
            endpoint=endpoint
        )

        db.add(log)

        await db.commit()

        await db.refresh(log)

        return log