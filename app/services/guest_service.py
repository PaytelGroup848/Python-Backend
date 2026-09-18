import logging
import uuid
from typing import Optional, Tuple

from jose import jwt, JWTError
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM,
)
import app.db.database as db_module
from app.models.user import User
from app.models.session import Session as UserSession
from app.models.conversation_session import ConversationSession
from app.models.conversation import Conversation
from app.models.generated_image import GeneratedImage
from app.models.guest_refund_job import GuestRefundJob
from app.shared.redis.client import redis_client

logger = logging.getLogger(__name__)

# =====================================================================
# GUEST QUOTA CONSTANTS & INVARIANTS
# =====================================================================
GUEST_MAX_CREDITS = 3
GUEST_QUOTA_TTL = 604800          # 7 days in seconds
GUEST_REFUND_MARKER_TTL = 604800  # 7 days in seconds (matches quota)
GUEST_INIT_MAP_TTL = 86400        # 24 hours deduplication window

# =====================================================================
# ATOMIC REDIS LUA SCRIPTS
# =====================================================================
# 1. Atomic Reservation Script
# Returns:
#   {-1, 0} -> Quota key missing or expired (NEVER recreate!)
#   {0, 0}  -> Quota exhausted (already <= 0)
#   {1, remaining} -> Successfully reserved 1 credit
RESERVE_CREDIT_LUA = """
local current = redis.call('get', KEYS[1])
if not current then
    return {-1, 0}
end
current = tonumber(current)
if not current then
    return {-1, 0}
end
if current <= 0 then
    return {0, 0}
end
local remaining = redis.call('decr', KEYS[1])
if remaining < 0 then
    remaining = 0
end
return {1, remaining}
"""

# 2. Marker-First Idempotent Refund Script
# Returns:
#   {0, current}   -> Already refunded or already capped at max
#   {-1, 0}        -> Quota key missing (NEVER recreate on refund!)
#   {1, new_val}   -> Successfully refunded and incremented
REFUND_CREDIT_LUA = """
local already_refunded = redis.call('get', KEYS[2])
if already_refunded then
    local cur = redis.call('get', KEYS[1])
    return {0, cur and tonumber(cur) or 0}
end
redis.call('set', KEYS[2], '1', 'EX', tonumber(ARGV[2]))
local current = redis.call('get', KEYS[1])
if not current then
    return {-1, 0}
end
current = tonumber(current)
if not current then
    return {-1, 0}
end
if current < tonumber(ARGV[1]) then
    local new_val = redis.call('incr', KEYS[1])
    return {1, new_val}
else
    return {0, current}
end
"""


async def get_guest_credits(user_id: int | str) -> Optional[int]:
    """
    Reads the current available guest credits from Redis.
    Returns integer credit count or None if key is absent/expired.
    """
    try:
        val = await redis_client.get(f"guest:credits:{user_id}")
        if val is not None:
            try:
                return int(val)
            except (ValueError, TypeError):
                return 0
        return None
    except Exception as e:
        logger.error(f"Failed reading guest credits for user {user_id}: {e}")
        return None


async def reserve_guest_credit(user_id: int | str) -> Tuple[int, int]:
    """
    Atomically reserves 1 guest credit using the single-threaded Redis Lua script.
    Returns:
        (1, remaining): Successfully decremented credit
        (0, 0): Quota limit reached
        (-1, 0): Quota key missing/expired
    """
    quota_key = f"guest:credits:{user_id}"
    try:
        res = await redis_client.eval(RESERVE_CREDIT_LUA, 1, quota_key)
        if isinstance(res, (list, tuple)) and len(res) >= 2:
            return int(res[0]), int(res[1])
        return 0, 0
    except Exception as e:
        logger.exception(f"Redis reservation error for guest {user_id}: {e}")
        # Fail safe on Redis outage: treat as missing quota to prevent uncontrolled bypass
        return -1, 0


async def record_failed_refund_job(
    user_id: int | str,
    request_id: str,
    reason: Optional[str] = None,
    error: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> bool:
    """
    Persists a durable guest refund job in PostgreSQL when Redis is unavailable.
    Guarantees:
      - DB Unique constraint on request_id prevents duplicate job creation.
      - Never recreates missing quota keys.
      - Provides an audit trail and work queue for the durable refund worker.
    """
    try:
        clean_user_id = int(user_id)
    except (ValueError, TypeError):
        logger.error(f"Cannot record durable refund job: invalid user_id '{user_id}'")
        return False

    stmt = pg_insert(GuestRefundJob).values(
        guest_user_id=clean_user_id,
        request_id=str(request_id),
        reason=reason or "redis_refund_outage",
        status="PENDING",
        attempt_count=0,
        next_attempt_at=datetime.utcnow(),
        last_error=str(error) if error else "Redis unavailable during refund",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    ).on_conflict_do_nothing(index_elements=["request_id"])

    if db is not None and db.is_active:
        try:
            await db.execute(stmt)
            await db.commit()
            logger.info(f"Durable refund job persisted for guest {clean_user_id} req {request_id} via active session")
            return True
        except Exception as db_err:
            logger.exception(f"Failed to record durable refund job via active session: {db_err}")
            await db.rollback()

    # Fallback to independent session
    try:
        async with db_module.AsyncSessionLocal() as session:
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Durable refund job persisted for guest {clean_user_id} req {request_id} via independent session")
            return True
    except Exception as fallback_err:
        logger.exception(f"CRITICAL: Failed persisting durable refund job for guest {clean_user_id} req {request_id}: {fallback_err}")
        return False


async def refund_guest_credit(
    user_id: int | str,
    request_id: str,
    db: Optional[AsyncSession] = None,
    reason: Optional[str] = None,
) -> Tuple[int, int]:
    """
    Atomically refunds 1 guest credit using the marker-first idempotent Lua script.
    Guarantees:
      - Idempotent: Subsequent calls with the same request_id return {0, current}
      - Capped: Quota never exceeds GUEST_MAX_CREDITS (3)
      - Never recreates missing quota keys: Returns {-1, 0} if quota key is gone
      - Durable: If Redis is unavailable, persists a job to PostgreSQL guest_refund_jobs table.
    Returns:
        (1, new_val): Refund applied
        (0, cur): Already refunded or capped
        (-1, 0): Quota key missing
    """
    quota_key = f"guest:credits:{user_id}"
    marker_key = f"guest:refunded:{request_id}"
    try:
        res = await redis_client.eval(
            REFUND_CREDIT_LUA,
            2,
            quota_key,
            marker_key,
            str(GUEST_MAX_CREDITS),
            str(GUEST_REFUND_MARKER_TTL)
        )
        if isinstance(res, (list, tuple)) and len(res) >= 2:
            return int(res[0]), int(res[1])
        return 0, 0
    except Exception as e:
        logger.exception(f"Redis refund error for guest {user_id} req {request_id}: {e}")
        # Persist durable refund job in PostgreSQL so credit is never silently lost
        await record_failed_refund_job(
            user_id=user_id,
            request_id=request_id,
            reason=reason or "redis_outage",
            error=str(e),
            db=db,
        )
        return 0, 0


async def initialize_guest_user(
    db: AsyncSession,
    guest_init_id: Optional[str] = None
) -> Tuple[User, str, str]:
    """
    Provisions or re-identifies a guest session with fail-safe initialization.
    - guest_init_id: correlation key used solely for retry deduplication.
    Flow:
      1. If guest_init_id provided, check Redis mapping for existing guest.
      2. If mapped guest still exists in DB and has active quota, return fresh token.
      3. Otherwise, create new shadow User, flush DB, set Redis quota (3 credits, 7d).
      4. Issue stateless JWT access & refresh tokens with role='guest'.
      5. Save UserSession in DB and commit.
      6. If commit fails, symmetrically clean up Redis quota key and rollback DB.
    """
    # 1. Deduplication lookup if correlation ID provided
    if guest_init_id and guest_init_id.strip():
        clean_init_id = guest_init_id.strip()
        try:
            cached_id = await redis_client.get(f"guest:init_map:{clean_init_id}")
            if cached_id:
                user_res = await db.execute(
                    select(User).where(User.id == int(cached_id))
                )
                existing_user = user_res.scalar_one_or_none()
                if existing_user and existing_user.role == "guest":
                    quota = await get_guest_credits(existing_user.id)
                    if quota is not None:
                        # Existing guest session is still valid
                        access_token = create_access_token({
                            "sub": str(existing_user.id),
                            "role": "guest"
                        })
                        refresh_token = create_refresh_token({
                            "sub": str(existing_user.id),
                            "role": "guest"
                        })
                        # Ensure session row exists
                        session_res = await db.execute(
                            select(UserSession).where(UserSession.user_id == existing_user.id)
                        )
                        if not session_res.scalars().first():
                            db.add(UserSession(user_id=existing_user.id, refresh_token=refresh_token))
                            await db.commit()

                        return existing_user, access_token, refresh_token
        except Exception as lookup_err:
            logger.warning(f"Guest provisioning deduplication lookup failed: {lookup_err}")

    # 2. Fresh guest creation
    unique_suffix = uuid.uuid4().hex
    shadow_email = f"guest_{unique_suffix[:12]}@guest.internal"
    guest_user = User(
        name="Guest Visitor",
        email=shadow_email,
        password=None,
        role="guest",
        is_active=True
    )

    db.add(guest_user)
    await db.flush()  # Allocates guest_user.id
    guest_id = guest_user.id

    # 3. Redis Quota Initialization with symmetric cleanup on failure
    quota_initialized = False
    try:
        await redis_client.set(
            f"guest:credits:{guest_id}",
            str(GUEST_MAX_CREDITS),
            ex=GUEST_QUOTA_TTL
        )
        quota_initialized = True
        if guest_init_id and guest_init_id.strip():
            await redis_client.set(
                f"guest:init_map:{guest_init_id.strip()}",
                str(guest_id),
                ex=GUEST_INIT_MAP_TTL
            )
    except Exception as redis_err:
        logger.error(f"Redis quota initialization failed for guest {guest_id}: {redis_err}")
        await db.rollback()
        raise RuntimeError("Service temporarily unavailable: Failed to initialize guest quota")

    # 4. Issue tokens & create DB Session
    access_token = create_access_token({
        "sub": str(guest_id),
        "role": "guest"
    })
    refresh_token = create_refresh_token({
        "sub": str(guest_id),
        "role": "guest"
    })

    user_session = UserSession(
        user_id=guest_id,
        refresh_token=refresh_token
    )
    db.add(user_session)

    # 5. Atomic DB commit with symmetric cleanup
    try:
        await db.commit()
        await db.refresh(guest_user)
        logger.info(f"Successfully provisioned guest user id={guest_id}")
        return guest_user, access_token, refresh_token
    except Exception as commit_err:
        logger.error(f"Failed committing guest user {guest_id}: {commit_err}")
        await db.rollback()
        if quota_initialized:
            try:
                await redis_client.delete(f"guest:credits:{guest_id}")
                if guest_init_id:
                    await redis_client.delete(f"guest:init_map:{guest_init_id.strip()}")
            except Exception:
                pass
        raise commit_err


async def transfer_guest_data(
    db: AsyncSession,
    guest_token: Optional[str],
    target_user_id: int
) -> bool:
    """
    Two-Factor Authenticated Guest Data Migration with Row-Locking Concurrency Control.
    Safeguards:
      1. Cryptographic Factor: JWT signature, expiration, and role == 'guest'.
      2. Database Factor: Active UserSession in DB for guest_user_id.
      3. Row Lock: SELECT ... FOR UPDATE on guest user to prevent concurrent race conditions.
      4. Complete FK Reassignment:
         - conversation_sessions.user_id -> target_user_id
         - conversations.user_id -> target_user_id
         - generated_images.user_id -> target_user_id (prevents ON DELETE CASCADE wipe)
      5. Deletes guest sessions and shadow user.
      6. Post-commit Redis quota and marker cleanup.
    """
    if not guest_token or not guest_token.strip():
        return False

    clean_token = guest_token.strip()
    if clean_token.lower().startswith("bearer "):
        clean_token = clean_token[7:].strip()

    # Factor 1: Cryptographic JWT Verification
    try:
        payload = jwt.decode(clean_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        logger.warning(f"Guest migration rejected: Invalid or expired JWT: {e}")
        return False

    role = payload.get("role")
    if role != "guest":
        logger.warning(f"Guest migration rejected: Token role is '{role}', expected 'guest'")
        return False

    guest_sub = payload.get("sub")
    if not guest_sub:
        logger.warning("Guest migration rejected: Missing 'sub' claim")
        return False

    try:
        guest_user_id = int(guest_sub)
    except (ValueError, TypeError):
        logger.warning(f"Guest migration rejected: Invalid sub claim format '{guest_sub}'")
        return False

    if guest_user_id == target_user_id:
        return False

    # Factor 2: Database Session Verification & Concurrency Row-Locking
    try:
        # Check active session exists
        session_res = await db.execute(
            select(UserSession).where(UserSession.user_id == guest_user_id)
        )
        if not session_res.scalars().first():
            logger.info(f"Guest migration: No active session for guest_user_id={guest_user_id} (already migrated)")
            return False

        # Acquire exclusive row lock on shadow guest user
        guest_user_res = await db.execute(
            select(User).where(User.id == guest_user_id).with_for_update()
        )
        guest_user = guest_user_res.scalar_one_or_none()
        if not guest_user or guest_user.role != "guest":
            logger.warning(f"Guest migration: Guest user {guest_user_id} not found or role != guest")
            return False

        # Reassign conversation_sessions
        await db.execute(
            update(ConversationSession)
            .where(ConversationSession.user_id == guest_user_id)
            .values(user_id=target_user_id)
        )

        # Reassign conversations (audit table)
        await db.execute(
            update(Conversation)
            .where(Conversation.user_id == guest_user_id)
            .values(user_id=target_user_id)
        )

        # Reassign generated_images to prevent ON DELETE CASCADE wipe
        await db.execute(
            update(GeneratedImage)
            .where(GeneratedImage.user_id == guest_user_id)
            .values(user_id=target_user_id)
        )

        # Delete guest user sessions
        await db.execute(
            delete(UserSession).where(UserSession.user_id == guest_user_id)
        )

        # Delete shadow guest user
        await db.delete(guest_user)

        # Commit transactional changes
        await db.commit()
        logger.info(
            f"Successfully migrated guest data from guest_user_id={guest_user_id} to target_user_id={target_user_id}"
        )

    except Exception as migration_err:
        await db.rollback()
        logger.exception(f"Guest migration failed for guest_user_id={guest_user_id}: {migration_err}")
        return False

    # Post-Commit Redis Quota Cleanup
    try:
        await redis_client.delete(f"guest:credits:{guest_user_id}")
    except Exception as redis_clean_err:
        logger.warning(f"Post-commit Redis cleanup warning for guest {guest_user_id}: {redis_clean_err}")

    return True
