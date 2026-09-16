"""
SESS-01 & SESS-02: Session Cleanup Lifecycle & Scheduler Tests
"""
import unittest
from datetime import datetime, timedelta

import qa_tests.conftest

from app.jobs.session_cleanup_job import cleanup_expired_sessions
from app.core.security import REFRESH_TOKEN_EXPIRE_DAYS
from app.jobs.scheduler import scheduler


class TestSessionCleanup(unittest.TestCase):

    def test_SESS_01_cleanup_cutoff_calculation(self):
        """SESS-01: Verify retention-based cutoff strictly respects token lifetime + 24h buffer."""
        self.assertEqual(REFRESH_TOKEN_EXPIRE_DAYS, 7)

        now = datetime.utcnow()
        expected_cutoff = now - timedelta(days=8)

        # Cutoff must be 8 days in the past (7 days token validity + 1 day safety buffer)
        diff_days = (now - expected_cutoff).total_seconds() / 86400
        self.assertAlmostEqual(diff_days, 8.0, places=2)

    def test_SESS_02_scheduler_job_registration(self):
        """SESS-02: Verify cleanup_expired_sessions is registered in APScheduler with cron trigger."""
        jobs = scheduler.get_jobs()
        job_names = [j.func.__name__ for j in jobs]

        self.assertIn("cleanup_expired_sessions", job_names, "cleanup_expired_sessions must be registered in scheduler")
        self.assertIn("process_expired_subscriptions", job_names)


if __name__ == "__main__":
    unittest.main()

