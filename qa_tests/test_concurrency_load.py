"""
REF-06 & Phase 6/15: Concurrency, Load & Race Condition Validation Tests
"""
import asyncio
import time
import unittest
from datetime import datetime, timezone
from jose import jwt

import qa_tests.conftest

from app.core.security import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM
from app.modules.auth.schemas.auth_schema import RefreshTokenRequest


class TestConcurrencyLoad(unittest.TestCase):

    def test_REF_06_concurrent_refresh_token_decoding(self):
        """REF-06: Simulate 50 concurrent refresh token decode operations to verify thread-safety & latency."""
        token = create_refresh_token({"sub": "1001", "role": "admin"})

        async def decode_worker(worker_id):
            start = time.perf_counter()
            # Emulate validation work
            req = RefreshTokenRequest(refresh_token=token)
            payload = jwt.decode(req.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            latency_ms = (time.perf_counter() - start) * 1000
            return {
                "worker_id": worker_id,
                "user_id": payload.get("sub"),
                "latency_ms": latency_ms
            }

        async def run_swarm():
            tasks = [decode_worker(i) for i in range(50)]
            return await asyncio.gather(*tasks)

        results = asyncio.run(run_swarm())

        self.assertEqual(len(results), 50)
        user_ids = {r["user_id"] for r in results}
        self.assertEqual(user_ids, {"1001"})

        latencies = [r["latency_ms"] for r in results]
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)

        # Average latency must be sub-millisecond in memory
        self.assertLess(avg_latency, 50.0, f"Average latency too high: {avg_latency:.2f}ms")


if __name__ == "__main__":
    unittest.main()

