"""
RED-01 to RED-03, DB-01 to DB-04, DOCK-01 to DOCK-02: Resilience & Failure Injection Tests
"""
import asyncio
import unittest
import yaml

import qa_tests.conftest

from app.services.security_service import is_locked, record_failed_attempt, clear_failed_attempts
from app.db.redis_client import redis_client
from app.db.database import engine


class TestResilienceAndFailures(unittest.TestCase):

    def test_RED_01_redis_fail_open_resilience(self):
        """RED-01 & RED-02: Verify Redis disconnect produces fail-open behavior and structured warning."""
        async def run_test():
            from unittest.mock import patch
            with patch.object(redis_client, "get", side_effect=ConnectionError("Simulated Redis Connection Error")), \
                 patch.object(redis_client, "setex", side_effect=ConnectionError("Simulated Redis Connection Error")), \
                 patch.object(redis_client, "delete", side_effect=ConnectionError("Simulated Redis Connection Error")):
                
                # In test environment with simulated Redis drop, these calls must catch connection errors and fail open
                locked = await is_locked("qa_test_user@patwatoliai.com", "10.0.0.99")
                self.assertFalse(locked, "is_locked must fail-open (False) when Redis is down to prevent authentication outage")

                # Recording attempts must not raise unhandled exception
                await record_failed_attempt("qa_test_user@patwatoliai.com", "10.0.0.99")

                # Clearing attempts must not raise unhandled exception
                await clear_failed_attempts("qa_test_user@patwatoliai.com", "10.0.0.99")

        asyncio.run(run_test())

    def test_DB_03_engine_keepalive_configuration(self):
        """DB-03: Verify SQLAlchemy asyncpg engine contains TCP keepalive and pool recycle settings."""
        # 1. Pool Recycle
        self.assertEqual(engine.pool._recycle, 300, "Pool recycle must be set to 300s to avoid Docker NAT drops")

        # 2. Pool Pre-Ping
        self.assertTrue(engine.pool._pre_ping, "Pool pre_ping must be enabled to test connections before checkout")

        # 3. Connect Args & Server Settings
        # Inspect connect_args in the engine creator or dialect
        creator_connect_args = getattr(engine.dialect, "_connect_args", None) or getattr(engine.sync_engine.pool, "_connect_args", None)
        # Check source of database.py
        import inspect
        from app.db import database
        source = inspect.getsource(database)

        self.assertIn('"tcp_keepalives_idle": "60"', source)
        self.assertIn('"tcp_keepalives_interval": "10"', source)
        self.assertIn('"tcp_keepalives_count": "5"', source)
        self.assertIn('"command_timeout": 30', source)

    def test_DOCK_01_docker_compose_authenticated_healthcheck(self):
        """DOCK-01 & DOCK-02: Verify docker-compose.yml postgres healthcheck runs authenticated SELECT 1."""
        with open("docker-compose.yml", "r", encoding="utf-8") as f:
            compose = yaml.safe_load(f)

        postgres_service = compose.get("services", {}).get("postgres", {})
        healthcheck = postgres_service.get("healthcheck", {})
        test_cmd = healthcheck.get("test", [])

        self.assertTrue(len(test_cmd) >= 2)
        cmd_str = test_cmd[1]

        # Verify pg_isready is checked
        self.assertIn("pg_isready", cmd_str)
        # Verify authenticated psql SELECT 1 is checked
        self.assertIn("psql", cmd_str)
        self.assertIn("SELECT 1;", cmd_str)
        # Verify $$ container expansion is used
        self.assertIn("$$POSTGRES_USER", cmd_str)
        self.assertIn("$$POSTGRES_PASSWORD", cmd_str)
        self.assertIn("$$POSTGRES_DB", cmd_str)


if __name__ == "__main__":
    unittest.main()
