"""
Enterprise QA Test Suite for G25: Durable PostgreSQL Refund Recovery & Crash Resilience.
Strict Constraints:
  - DO NOT mock Redis/PostgreSQL for concurrency or persistence tests.
  - Tests execute against live PostgreSQL (port 5433) and live Redis (port 6379).
  - Proves end-to-end flow: Outage -> Durable Job Persisted -> Recovery -> Quota Restored -> COMPLETED.
"""
import os
import sys
import time
import uuid
import asyncio
import unittest
from datetime import datetime, timedelta

# Point environment to live local Docker container ports
os.environ["REDIS_HOST"] = "127.0.0.1"
os.environ["REDIS_PORT"] = "6379"
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/ai_llm_db"
os.environ["DATABASE_URL"] = DATABASE_URL

import qa_tests.conftest
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text, delete

import app.shared.redis.client as shared_r
import app.services.guest_service as gs
import app.services.guest_refund_worker as rw

from app.models.guest_refund_job import GuestRefundJob
from app.models.user import User
from app.models.session import Session as UserSession
from app.services.guest_service import (
    initialize_guest_user,
    reserve_guest_credit,
    refund_guest_credit,
    get_guest_credits,
    record_failed_refund_job,
    REFUND_CREDIT_LUA,
    GUEST_MAX_CREDITS,
    GUEST_REFUND_MARKER_TTL,
)
from app.services.guest_refund_worker import claim_and_process_refund_batch


class TestDurableRefundRecovery(unittest.IsolatedAsyncioTestCase):
    """Verifies all crash, outage, concurrency, and durability semantics of G25."""

    async def asyncSetUp(self):
        self.engine = create_async_engine(DATABASE_URL, echo=False)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        import app.db.database as app_db
        app_db.AsyncSessionLocal = self.async_session
        self.redis = aioredis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
        shared_r.redis_client = self.redis
        gs.redis_client = self.redis
        rw.redis_client = self.redis
        await self.redis.ping()

        # Clean existing test jobs from DB to ensure clean isolation
        async with self.async_session() as db:
            await db.execute(delete(GuestRefundJob))
            await db.commit()

    async def asyncTearDown(self):
        gs.redis_client = self.redis
        rw.redis_client = self.redis
        await self.redis.aclose()
        await self.engine.dispose()

    async def test_01_outage_creates_durable_postgresql_job_and_recovery_restores_credit(self):
        """
        G25 Core Test:
        1. Reserve credit: 3 -> 2.
        2. Simulate Redis connection timeout during refund attempt.
        3. Verify durable job persisted in PostgreSQL guest_refund_jobs table.
        4. Restore Redis connection.
        5. Run worker: claim_and_process_refund_batch().
        6. Verify job transitions to COMPLETED.
        7. Verify guest quota in Redis is restored from 2 -> 3.
        """
        async with self.async_session() as db:
            guest_user, guest_token, _ = await initialize_guest_user(db)
            guest_id = guest_user.id

        # 1. Reserve 1 credit -> 2 remaining
        res_st, rem = await reserve_guest_credit(guest_id)
        self.assertEqual(res_st, 1)
        self.assertEqual(rem, 2)
        self.assertEqual(await get_guest_credits(guest_id), 2)

        # 2. Simulate Redis outage during refund attempt
        req_id = f"test_outage_req_{uuid.uuid4().hex}"
        dead_redis = aioredis.Redis(host="127.0.0.1", port=6399, socket_connect_timeout=0.1)
        gs.redis_client = dead_redis

        # Attempt refund -> will catch Redis timeout and persist to PostgreSQL
        status, new_val = await refund_guest_credit(guest_id, req_id, reason="unit_test_outage")
        self.assertEqual(status, 0)
        self.assertEqual(new_val, 0)

        # 3. Verify job persisted in PostgreSQL
        async with self.async_session() as db:
            job = (await db.execute(select(GuestRefundJob).where(GuestRefundJob.request_id == req_id))).scalar_one_or_none()
            self.assertIsNotNone(job, "Durable refund job MUST be persisted in PostgreSQL on Redis failure")
            self.assertEqual(job.guest_user_id, guest_id)
            self.assertEqual(job.status, "PENDING")
            self.assertEqual(job.attempt_count, 0)
            self.assertEqual(job.reason, "unit_test_outage")

        # 4. Restore Redis connection
        gs.redis_client = self.redis
        rw.redis_client = self.redis

        # Prior to worker run, quota is still decremented at 2
        self.assertEqual(await get_guest_credits(guest_id), 2)

        # 5. Run worker to claim and process the durable job
        processed = await claim_and_process_refund_batch(worker_id="test-worker-1")
        self.assertGreaterEqual(processed, 1)

        # 6. Verify job is COMPLETED
        async with self.async_session() as db:
            job_after = (await db.execute(select(GuestRefundJob).where(GuestRefundJob.request_id == req_id))).scalar_one()
            self.assertEqual(job_after.status, "COMPLETED")
            self.assertIsNotNone(job_after.processed_at)
            self.assertIsNone(job_after.last_error)

        # 7. Verify Redis quota is restored to 3!
        self.assertEqual(await get_guest_credits(guest_id), 3)

        # Cleanup
        await self.redis.delete(f"guest:credits:{guest_id}", f"guest:refunded:{req_id}")

    async def test_02_duplicate_request_id_idempotent_job_persistence(self):
        """Verify DB UNIQUE constraint prevents duplicate refund jobs for the same request_id."""
        req_id = f"test_dup_{uuid.uuid4().hex}"
        ok1 = await record_failed_refund_job(101, req_id, reason="err1")
        ok2 = await record_failed_refund_job(101, req_id, reason="err2")

        self.assertTrue(ok1)
        self.assertTrue(ok2)

        async with self.async_session() as db:
            jobs = (await db.execute(select(GuestRefundJob).where(GuestRefundJob.request_id == req_id))).scalars().all()
            self.assertEqual(len(jobs), 1, "Duplicate request_id must NOT insert multiple job rows")

    async def test_03_concurrent_workers_skip_locked_zero_duplicate_processing(self):
        """Verify multiple parallel workers using FOR UPDATE SKIP LOCKED process disjoint jobs without conflict."""
        req_ids = [f"test_concur_{uuid.uuid4().hex}" for _ in range(6)]
        g_id = 202
        await self.redis.set(f"guest:credits:{g_id}", "0", ex=604800)

        for rid in req_ids:
            await record_failed_refund_job(g_id, rid, reason="concurrency_test")

        # Launch 3 workers concurrently to process the 6 jobs
        async def run_worker(w_id):
            return await claim_and_process_refund_batch(worker_id=w_id, limit=10)

        results = await asyncio.gather(
            run_worker("worker-A"),
            run_worker("worker-B"),
            run_worker("worker-C"),
        )

        total_processed = sum(results)
        self.assertEqual(total_processed, 6, "All 6 jobs must be processed exactly once across the 3 workers")

        # Verify all jobs are COMPLETED
        async with self.async_session() as db:
            completed_jobs = (await db.execute(
                select(GuestRefundJob).where(GuestRefundJob.request_id.in_(req_ids))
            )).scalars().all()
            self.assertEqual(len(completed_jobs), 6)
            for j in completed_jobs:
                self.assertEqual(j.status, "COMPLETED")

        # Quota capped at 3 credits
        quota = await get_guest_credits(g_id)
        self.assertEqual(quota, 3)

        # Cleanup
        await self.redis.delete(f"guest:credits:{g_id}")
        for rid in req_ids:
            await self.redis.delete(f"guest:refunded:{rid}")

    async def test_04_abandoned_lease_recovery_after_worker_crash(self):
        """
        Verify that a job left in PROCESSING state by a crashed worker is automatically
        recovered and processed by another worker once the lease expires.
        """
        req_id = f"test_abandoned_{uuid.uuid4().hex}"
        g_id = 303
        await self.redis.set(f"guest:credits:{g_id}", "1", ex=604800)

        # Insert job in PROCESSING state with locked_at 120 seconds in the past (lease expired)
        async with self.async_session() as db:
            crashed_job = GuestRefundJob(
                guest_user_id=g_id,
                request_id=req_id,
                status="PROCESSING",
                next_attempt_at=datetime.utcnow(),
                locked_at=datetime.utcnow() - timedelta(seconds=120),
                locked_by="crashed-worker-99",
                attempt_count=1,
            )
            db.add(crashed_job)
            await db.commit()

        # Alive worker runs and recovers the abandoned job
        processed = await claim_and_process_refund_batch(worker_id="alive-worker-1")
        self.assertGreaterEqual(processed, 1)

        async with self.async_session() as db:
            recovered_job = (await db.execute(
                select(GuestRefundJob).where(GuestRefundJob.request_id == req_id)
            )).scalar_one()
            self.assertEqual(recovered_job.status, "COMPLETED")

        # Quota restored from 1 -> 2
        self.assertEqual(await get_guest_credits(g_id), 2)

        # Cleanup
        await self.redis.delete(f"guest:credits:{g_id}", f"guest:refunded:{req_id}")

    async def test_05_crashed_after_redis_refund_before_db_update_idempotent_recovery(self):
        """
        Simulate crash where Redis refund succeeded (marker key created and quota incremented),
        but worker crashed before committing COMPLETED to PostgreSQL.
        The next worker run must see already_refunded in Redis Lua and mark COMPLETED without double-crediting.
        """
        req_id = f"test_post_redis_crash_{uuid.uuid4().hex}"
        g_id = 404
        await self.redis.set(f"guest:credits:{g_id}", "1", ex=604800)

        # 1. Lua script executed in Redis (simulating first worker succeeding on Redis)
        res = await self.redis.eval(
            REFUND_CREDIT_LUA, 2, f"guest:credits:{g_id}", f"guest:refunded:{req_id}", "3", "604800"
        )
        self.assertEqual(res, [1, 2])
        self.assertEqual(await get_guest_credits(g_id), 2)

        # 2. Worker crashed! DB still has job as PROCESSING with expired lease
        now = datetime.utcnow()
        past = now - timedelta(seconds=120)
        async with self.async_session() as db:
            job = GuestRefundJob(
                guest_user_id=g_id,
                request_id=req_id,
                status="PROCESSING",
                next_attempt_at=now,
                locked_at=past,
                locked_by="crashed-worker-x",
                created_at=past,
                updated_at=past,
            )
            db.add(job)
            await db.commit()

        # 3. New worker recovers the job
        processed = await claim_and_process_refund_batch(worker_id="recovery-worker")
        self.assertGreaterEqual(processed, 1)

        # 4. Verify job is marked COMPLETED
        async with self.async_session() as db:
            j = (await db.execute(select(GuestRefundJob).where(GuestRefundJob.request_id == req_id))).scalar_one()
            self.assertEqual(j.status, "COMPLETED")

        # 5. CRITICAL: Quota MUST STILL BE 2 (NOT double-incremented to 3!)
        self.assertEqual(await get_guest_credits(g_id), 2)

        # Cleanup
        await self.redis.delete(f"guest:credits:{g_id}", f"guest:refunded:{req_id}")

    async def test_06_missing_quota_key_never_recreated_by_worker(self):
        """Verify that when quota key is absent/expired in Redis, the worker marks COMPLETED without recreating key."""
        req_id = f"test_missing_{uuid.uuid4().hex}"
        g_id = 505
        # Ensure key absent
        await self.redis.delete(f"guest:credits:{g_id}")

        await record_failed_refund_job(g_id, req_id, reason="missing_key_test")
        processed = await claim_and_process_refund_batch()
        self.assertGreaterEqual(processed, 1)

        async with self.async_session() as db:
            job = (await db.execute(select(GuestRefundJob).where(GuestRefundJob.request_id == req_id))).scalar_one()
            self.assertEqual(job.status, "COMPLETED")
            self.assertIn("Quota key absent or expired", job.last_error)

        # Key MUST NOT have been recreated in Redis
        exists = await self.redis.exists(f"guest:credits:{g_id}")
        self.assertEqual(exists, 0, "Missing quota key must NEVER be recreated during durable refund recovery!")


if __name__ == "__main__":
    unittest.main()
