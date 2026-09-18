import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, update, or_, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.database as db_module
from app.models.guest_refund_job import GuestRefundJob
from app.services.guest_service import (
    REFUND_CREDIT_LUA,
    GUEST_MAX_CREDITS,
    GUEST_REFUND_MARKER_TTL,
)
from app.shared.redis.client import redis_client

logger = logging.getLogger(__name__)

# =====================================================================
# DURABLE REFUND WORKER CONSTANTS & POLICIES
# =====================================================================
CLAIM_BATCH_SIZE = 10
LOCK_LEASE_SECONDS = 60          # Lease timeout for recovering abandoned/crashed jobs
MAX_ATTEMPTS = 10                # Bounded retry count before transitioning to FAILED
BASE_BACKOFF_SECONDS = 5         # Initial retry delay
MAX_BACKOFF_SECONDS = 3600       # Maximum capped retry delay (1 hour)


async def claim_and_process_refund_batch(
    worker_id: Optional[str] = None,
    limit: int = CLAIM_BATCH_SIZE
) -> int:
    """
    Claims and processes a batch of eligible guest refund jobs.
    Guarantees:
      - PostgreSQL FOR UPDATE SKIP LOCKED prevents concurrent double-processing across workers.
      - Automatically re-claims jobs abandoned by crashed workers (locked_at older than lease).
      - Reuses the authoritative REFUND_CREDIT_LUA script.
      - Marks COMPLETED only after confirmed idempotent refund response from Redis.
      - Applies bounded exponential backoff on transient Redis failures.
    Returns:
      Number of jobs processed in this execution.
    """
    w_id = worker_id or f"refund-worker-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow()
    lease_cutoff = now - timedelta(seconds=LOCK_LEASE_SECONDS)

    claimed_job_ids = []

    # Step 1: Claim eligible jobs with row-level locking (SKIP LOCKED)
    async with db_module.AsyncSessionLocal() as db:
        try:
            # Query eligible jobs:
            # 1. PENDING with next_attempt_at <= now
            # 2. PROCESSING with locked_at <= lease_cutoff (crash recovery)
            claim_query = (
                select(GuestRefundJob.id)
                .where(
                    or_(
                        and_(
                            GuestRefundJob.status == "PENDING",
                            GuestRefundJob.next_attempt_at <= now,
                        ),
                        and_(
                            GuestRefundJob.status == "PROCESSING",
                            GuestRefundJob.locked_at <= lease_cutoff,
                        ),
                    )
                )
                .where(GuestRefundJob.status.notin_(["COMPLETED", "FAILED"]))
                .order_by(GuestRefundJob.next_attempt_at.asc())
                .limit(limit)
                .with_for_update(skip_locked=True)
            )

            result = await db.execute(claim_query)
            claimed_job_ids = list(result.scalars().all())

            if claimed_job_ids:
                # Mark claimed rows as PROCESSING under this worker's lease
                await db.execute(
                    update(GuestRefundJob)
                    .where(GuestRefundJob.id.in_(claimed_job_ids))
                    .values(
                        status="PROCESSING",
                        locked_at=now,
                        locked_by=w_id,
                        updated_at=now,
                    )
                )
                await db.commit()
                logger.info(f"Worker {w_id} successfully claimed {len(claimed_job_ids)} refund jobs: {claimed_job_ids}")
        except Exception as claim_err:
            logger.exception(f"Worker {w_id} failed claiming refund jobs: {claim_err}")
            await db.rollback()
            return 0

    if not claimed_job_ids:
        return 0

    # Step 2: Process each claimed job independently
    processed_count = 0
    for job_id in claimed_job_ids:
        async with db_module.AsyncSessionLocal() as db:
            try:
                job = await db.get(GuestRefundJob, job_id)
                if not job or job.status != "PROCESSING" or job.locked_by != w_id:
                    continue

                quota_key = f"guest:credits:{job.guest_user_id}"
                marker_key = f"guest:refunded:{job.request_id}"

                # Execute authoritative marker-first idempotent Lua script
                res = await redis_client.eval(
                    REFUND_CREDIT_LUA,
                    2,
                    quota_key,
                    marker_key,
                    str(GUEST_MAX_CREDITS),
                    str(GUEST_REFUND_MARKER_TTL)
                )

                op_status = int(res[0]) if isinstance(res, (list, tuple)) and len(res) >= 1 else 0
                new_val = int(res[1]) if isinstance(res, (list, tuple)) and len(res) >= 2 else 0

                finish_time = datetime.utcnow()

                if op_status == 1:
                    # Successfully refunded
                    job.status = "COMPLETED"
                    job.processed_at = finish_time
                    job.last_error = None
                    job.updated_at = finish_time
                    logger.info(f"Durable refund SUCCESS for guest {job.guest_user_id} req {job.request_id} -> new quota {new_val}")

                elif op_status == 0:
                    # Already refunded or quota capped at 3
                    job.status = "COMPLETED"
                    job.processed_at = finish_time
                    job.last_error = None
                    job.updated_at = finish_time
                    logger.info(f"Durable refund ALREADY_APPLIED/CAPPED for guest {job.guest_user_id} req {job.request_id} -> quota {new_val}")

                elif op_status == -1:
                    # Quota key missing in Redis -> NEVER recreate!
                    job.status = "COMPLETED"
                    job.processed_at = finish_time
                    job.last_error = "Quota key absent or expired in Redis; credit not recreated"
                    job.updated_at = finish_time
                    logger.warning(f"Durable refund QUOTA_KEY_MISSING for guest {job.guest_user_id} req {job.request_id}; completed without recreating key")

                await db.commit()
                processed_count += 1

            except Exception as proc_err:
                await db.rollback()
                logger.warning(f"Transient error processing refund job {job_id}: {proc_err}")

                # Record attempt and calculate exponential backoff
                async with db_module.AsyncSessionLocal() as err_db:
                    try:
                        err_job = await err_db.get(GuestRefundJob, job_id)
                        if err_job:
                            err_now = datetime.utcnow()
                            err_job.attempt_count += 1
                            err_job.last_error = str(proc_err)
                            err_job.updated_at = err_now

                            if err_job.attempt_count >= MAX_ATTEMPTS:
                                err_job.status = "FAILED"
                                logger.error(f"Durable refund job {job_id} permanently FAILED after {MAX_ATTEMPTS} attempts.")
                            else:
                                delay_sec = min(
                                    BASE_BACKOFF_SECONDS * (2 ** (err_job.attempt_count - 1)),
                                    MAX_BACKOFF_SECONDS
                                )
                                err_job.status = "PENDING"
                                err_job.next_attempt_at = err_now + timedelta(seconds=delay_sec)
                                err_job.locked_at = None
                                err_job.locked_by = None
                                logger.info(f"Refund job {job_id} scheduled for retry #{err_job.attempt_count} in {delay_sec}s")

                            await err_db.commit()
                    except Exception as fatal_e:
                        logger.exception(f"Fatal error updating failed refund job {job_id}: {fatal_e}")

    return processed_count


# Global worker control references
_refund_worker_task: Optional[asyncio.Task] = None
_refund_worker_stop_event: Optional[asyncio.Event] = None


async def run_refund_worker_loop(
    poll_interval: float = 10.0,
    stop_event: Optional[asyncio.Event] = None
):
    """
    Continuous background loop for draining and executing durable guest refund jobs.
    """
    worker_id = f"refund-worker-{uuid.uuid4().hex[:8]}"
    logger.info(f"Starting Guest Refund DLQ Worker: {worker_id} (poll interval: {poll_interval}s)")

    while stop_event is None or not stop_event.is_set():
        try:
            processed = await claim_and_process_refund_batch(worker_id=worker_id)
            if processed > 0:
                # If there was work, immediately check again for more
                await asyncio.sleep(0.5)
                continue
        except asyncio.CancelledError:
            logger.info(f"Guest Refund Worker {worker_id} cancelled cleanly.")
            break
        except Exception as e:
            logger.exception(f"Guest Refund Worker loop exception: {e}")

        try:
            await asyncio.sleep(poll_interval)
        except asyncio.CancelledError:
            break


def start_guest_refund_worker_task(poll_interval: float = 10.0) -> asyncio.Task:
    """Spawns the singleton background refund worker task."""
    global _refund_worker_task, _refund_worker_stop_event
    if _refund_worker_task is None or _refund_worker_task.done():
        _refund_worker_stop_event = asyncio.Event()
        _refund_worker_task = asyncio.create_task(
            run_refund_worker_loop(poll_interval=poll_interval, stop_event=_refund_worker_stop_event)
        )
        logger.info("Spawned singleton background guest refund worker task.")
    return _refund_worker_task


async def stop_guest_refund_worker_task():
    """Signals and cleanly cancels the singleton background refund worker task."""
    global _refund_worker_task, _refund_worker_stop_event
    if _refund_worker_stop_event:
        _refund_worker_stop_event.set()
    if _refund_worker_task and not _refund_worker_task.done():
        _refund_worker_task.cancel()
        try:
            await _refund_worker_task
        except asyncio.CancelledError:
            pass
    _refund_worker_task = None
    _refund_worker_stop_event = None
