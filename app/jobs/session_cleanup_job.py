import logging
from datetime import datetime, timedelta
from sqlalchemy import delete

from app.db.database import AsyncSessionLocal
from app.models.session import Session as UserSession
from app.core.security import REFRESH_TOKEN_EXPIRE_DAYS

logger = logging.getLogger(__name__)


async def cleanup_expired_sessions():
    """
    Retention-based cleanup job for expired authentication sessions.
    Sessions are eligible for deletion only after token lifetime (REFRESH_TOKEN_EXPIRE_DAYS)
    plus a 24-hour safety buffer, guaranteeing that no active session within its valid
    window is ever touched.
    """
    cutoff = datetime.utcnow() - timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS + 1)

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                delete(UserSession).where(UserSession.created_at < cutoff)
            )
            await db.commit()
            deleted_count = result.rowcount if hasattr(result, "rowcount") else "unknown"
            logger.info(
                f"Expired sessions cleanup completed successfully: {deleted_count} stale session(s) purged (cutoff: {cutoff.isoformat()})."
            )
        except Exception as e:
            await db.rollback()
            logger.warning(
                f"Expired sessions cleanup job encountered an error: {e}"
            )

