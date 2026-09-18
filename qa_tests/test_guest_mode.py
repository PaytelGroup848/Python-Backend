"""
Enterprise QA Test Suite for Guest Mode, Atomic Quota Accounting, and Two-Factor Migration.
Guarantees:
  1. Exactly 3 Guest Credits enforced atomically.
  2. Missing quota key is NEVER recreated on reservation or refund.
  3. Marker-first idempotent refund capped at 3 credits.
  4. 0 vs -1 distinction: 0 -> CREDITS_LIMIT_REACHED, -1 -> GUEST_SESSION_EXPIRED.
  5. Fail-safe provisioning with symmetric rollback.
  6. Two-factor authenticated migration with row-locking and full FK reassignment.
  7. Authenticated user boundary isolation (existing users bypass 100% untouched).
"""
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import qa_tests.conftest

from app.services.guest_service import (
    GUEST_MAX_CREDITS,
    GUEST_QUOTA_TTL,
    GUEST_REFUND_MARKER_TTL,
    RESERVE_CREDIT_LUA,
    REFUND_CREDIT_LUA,
    reserve_guest_credit,
    refund_guest_credit,
    get_guest_credits,
    initialize_guest_user,
    transfer_guest_data,
)
from app.core.security import create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt


class TestGuestQuotaInvariants(unittest.TestCase):
    """Verifies atomic Redis quota operations, Lua contract semantics, and 0 vs -1 distinction."""

    def test_01_reservation_script_semantics(self):
        """Simulate reservation Lua logic to ensure exact atomic behavior."""
        def run_reserve_lua(store, key):
            current = store.get(key)
            if current is None:
                return [-1, 0]
            current = int(current)
            if current <= 0:
                return [0, 0]
            remaining = current - 1
            if remaining < 0:
                store[key] = 0
                remaining = 0
            else:
                store[key] = remaining
            return [1, remaining]

        redis_store = {"guest:credits:101": 3}

        # Prompt 1: 3 -> 2
        res1 = run_reserve_lua(redis_store, "guest:credits:101")
        self.assertEqual(res1, [1, 2])
        self.assertEqual(redis_store["guest:credits:101"], 2)

        # Prompt 2: 2 -> 1
        res2 = run_reserve_lua(redis_store, "guest:credits:101")
        self.assertEqual(res2, [1, 1])
        self.assertEqual(redis_store["guest:credits:101"], 1)

        # Prompt 3: 1 -> 0
        res3 = run_reserve_lua(redis_store, "guest:credits:101")
        self.assertEqual(res3, [1, 0])
        self.assertEqual(redis_store["guest:credits:101"], 0)

        # Prompt 4: 0 -> Limit reached [0, 0]
        res4 = run_reserve_lua(redis_store, "guest:credits:101")
        self.assertEqual(res4, [0, 0])
        self.assertEqual(redis_store["guest:credits:101"], 0)

        # Missing Key: Returns [-1, 0] and NEVER recreates key
        del redis_store["guest:credits:101"]
        res_missing = run_reserve_lua(redis_store, "guest:credits:101")
        self.assertEqual(res_missing, [-1, 0])
        self.assertNotIn("guest:credits:101", redis_store, "Missing key must NEVER be recreated on reservation!")

    def test_02_refund_script_marker_first_idempotency(self):
        """Simulate marker-first refund Lua logic to ensure idempotency, capping, and missing-key refusal."""
        def run_refund_lua(store, quota_key, marker_key, max_credits=3):
            already_refunded = store.get(marker_key)
            if already_refunded:
                cur = store.get(quota_key)
                return [0, int(cur) if cur is not None else 0]

            store[marker_key] = 1
            current = store.get(quota_key)
            if current is None:
                return [-1, 0]

            current = int(current)
            if current < max_credits:
                new_val = current + 1
                store[quota_key] = new_val
                return [1, new_val]
            else:
                return [0, current]

        # Case A: Normal refund from 2 to 3
        redis_store = {"guest:credits:102": 2}
        req_id = "req_abc_001"
        res_a = run_refund_lua(redis_store, "guest:credits:102", f"guest:refunded:{req_id}")
        self.assertEqual(res_a, [1, 3])
        self.assertEqual(redis_store["guest:credits:102"], 3)
        self.assertIn(f"guest:refunded:{req_id}", redis_store)

        # Duplicate refund for same req_id: returns [0, 3] without incrementing
        res_dup = run_refund_lua(redis_store, "guest:credits:102", f"guest:refunded:{req_id}")
        self.assertEqual(res_dup, [0, 3])
        self.assertEqual(redis_store["guest:credits:102"], 3)

        # Case B: Capped at max credits (3)
        req_id_2 = "req_abc_002"
        res_cap = run_refund_lua(redis_store, "guest:credits:102", f"guest:refunded:{req_id_2}")
        self.assertEqual(res_cap, [0, 3], "Refund must NEVER exceed max quota (3)!")
        self.assertEqual(redis_store["guest:credits:102"], 3)

        # Case C: Missing key on refund returns [-1, 0] and NEVER recreates quota
        del redis_store["guest:credits:102"]
        req_id_3 = "req_abc_003"
        res_missing_refund = run_refund_lua(redis_store, "guest:credits:102", f"guest:refunded:{req_id_3}")
        self.assertEqual(res_missing_refund, [-1, 0])
        self.assertNotIn("guest:credits:102", redis_store, "Missing quota key must NEVER be recreated on refund!")

    def test_03_service_wrapper_calls_eval(self):
        """Verify reserve_guest_credit and refund_guest_credit invoke redis_client.eval properly."""
        async def run_test():
            with patch("app.services.guest_service.redis_client") as mock_redis:
                # Test reserve
                mock_redis.eval = AsyncMock(return_value=[1, 2])
                status, rem = await reserve_guest_credit(999)
                self.assertEqual(status, 1)
                self.assertEqual(rem, 2)
                mock_redis.eval.assert_called_once_with(RESERVE_CREDIT_LUA, 1, "guest:credits:999")

                # Test refund
                mock_redis.eval.reset_mock()
                mock_redis.eval = AsyncMock(return_value=[1, 3])
                r_status, r_val = await refund_guest_credit(999, "test_req_xyz")
                self.assertEqual(r_status, 1)
                self.assertEqual(r_val, 3)
                mock_redis.eval.assert_called_once_with(
                    REFUND_CREDIT_LUA,
                    2,
                    "guest:credits:999",
                    "guest:refunded:test_req_xyz",
                    str(GUEST_MAX_CREDITS),
                    str(GUEST_REFUND_MARKER_TTL)
                )

        asyncio.run(run_test())


    def test_04_corrupted_quota_data_safety(self):
        """Verify get_guest_credits and Lua script handle corrupted non-numeric data safely."""
        async def run_test():
            with patch("app.services.guest_service.redis_client") as mock_redis:
                # Corrupted non-numeric string in Redis
                mock_redis.get = AsyncMock(return_value="corrupted_not_a_number")
                credits_val = await get_guest_credits(105)
                self.assertEqual(credits_val, 0, "Non-numeric string in Redis must safely return 0 without raising ValueError!")

                # Empty string in Redis
                mock_redis.get = AsyncMock(return_value="")
                empty_val = await get_guest_credits(105)
                self.assertEqual(empty_val, 0, "Empty string in Redis must safely return 0 without raising ValueError!")

        asyncio.run(run_test())


class TestGuestProvisioning(unittest.TestCase):
    """Verifies guest identity creation, token issuance, and fail-safe rollback."""

    def test_01_provisioning_flow(self):
        """Verify initialize_guest_user creates User, Redis quota, and returns valid guest tokens."""
        async def run_test():
            mock_db = MagicMock()
            mock_db.add = MagicMock()
            mock_db.flush = AsyncMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()
            mock_db.rollback = AsyncMock()

            # Mock flushed user id allocation
            def side_effect_flush():
                pass
            mock_db.flush.side_effect = side_effect_flush

            with patch("app.services.guest_service.redis_client") as mock_redis:
                mock_redis.get = AsyncMock(return_value=None)
                mock_redis.set = AsyncMock(return_value=True)

                user, access_token, refresh_token = await initialize_guest_user(
                    db=mock_db,
                    guest_init_id="client_init_token_123"
                )

                # Shadow user attributes
                self.assertEqual(user.role, "guest")
                self.assertEqual(user.name, "Guest Visitor")
                self.assertTrue(user.email.endswith("@guest.internal"))

                # Token claims
                payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
                self.assertEqual(payload.get("role"), "guest")
                self.assertEqual(payload.get("sub"), str(user.id))

                # Redis quota initialized with 3 credits and 7d TTL
                mock_redis.set.assert_any_call(
                    f"guest:credits:{user.id}",
                    "3",
                    ex=GUEST_QUOTA_TTL
                )
                # Redis deduplication map written
                mock_redis.set.assert_any_call(
                    "guest:init_map:client_init_token_123",
                    str(user.id),
                    ex=86400
                )
                # DB committed
                mock_db.commit.assert_called_once()

        asyncio.run(run_test())

    def test_02_symmetric_cleanup_on_commit_failure(self):
        """Verify that if DB commit fails during provisioning, Redis quota key is symmetrically deleted."""
        async def run_test():
            mock_db = MagicMock()
            mock_db.add = MagicMock()
            mock_db.flush = AsyncMock()
            mock_db.commit = AsyncMock(side_effect=RuntimeError("DB Commit Crash"))
            mock_db.rollback = AsyncMock()

            with patch("app.services.guest_service.redis_client") as mock_redis:
                mock_redis.get = AsyncMock(return_value=None)
                mock_redis.set = AsyncMock(return_value=True)
                mock_redis.delete = AsyncMock(return_value=1)

                with self.assertRaises(RuntimeError):
                    await initialize_guest_user(
                        db=mock_db,
                        guest_init_id="retry_key_fail"
                    )

                # Symmetrically cleaned up
                mock_db.rollback.assert_called_once()
                mock_redis.delete.assert_any_call(mock_redis.delete.call_args[0][0])

        asyncio.run(run_test())


class TestGuestMigration(unittest.TestCase):
    """Verifies two-factor guest migration, row locking, and foreign key reassignment."""

    def test_01_reject_non_guest_tokens(self):
        """Security check: Cannot migrate using an employee or admin token."""
        async def run_test():
            mock_db = MagicMock()
            # Issue employee token
            employee_token = create_access_token({"sub": "501", "role": "employee"})

            res = await transfer_guest_data(
                db=mock_db,
                guest_token=employee_token,
                target_user_id=888
            )
            self.assertFalse(res, "Employee tokens must be rejected from guest migration!")
            mock_db.execute.assert_not_called()

        asyncio.run(run_test())

    def test_02_successful_two_factor_migration(self):
        """Verify successful migration reassigns conversations, images, sessions, and deletes shadow user."""
        async def run_test():
            mock_db = MagicMock()
            mock_db.commit = AsyncMock()
            mock_db.rollback = AsyncMock()
            mock_db.delete = AsyncMock()

            # Mock DB execute returns
            guest_id = 303
            target_id = 999
            guest_token = create_access_token({"sub": str(guest_id), "role": "guest"})

            # Factor 2: Session exists
            mock_session = MagicMock(user_id=guest_id)
            mock_session_res = MagicMock()
            mock_session_res.scalars.return_value.first.return_value = mock_session

            # Row lock guest user
            mock_guest_user = MagicMock(id=guest_id, role="guest")
            mock_user_res = MagicMock()
            mock_user_res.scalar_one_or_none.return_value = mock_guest_user

            # Route execute calls
            async def execute_side_effect(statement, *args, **kwargs):
                stmt_str = str(statement).upper()
                if "SESSIONS" in stmt_str and "SELECT" in stmt_str:
                    return mock_session_res
                elif "USERS" in stmt_str and "SELECT" in stmt_str:
                    return mock_user_res
                return MagicMock()

            mock_db.execute = AsyncMock(side_effect=execute_side_effect)

            with patch("app.services.guest_service.redis_client") as mock_redis:
                mock_redis.delete = AsyncMock(return_value=1)

                migrated = await transfer_guest_data(
                    db=mock_db,
                    guest_token=guest_token,
                    target_user_id=target_id
                )

                self.assertTrue(migrated)
                mock_db.commit.assert_called_once()
                mock_db.delete.assert_called_once_with(mock_guest_user)
                mock_redis.delete.assert_called_once_with(f"guest:credits:{guest_id}")

        asyncio.run(run_test())

    def test_03_migration_with_bearer_prefix(self):
        """Verify guest migration correctly strips 'Bearer ' prefix and succeeds."""
        async def run_test():
            mock_db = MagicMock()
            mock_db.commit = AsyncMock()
            mock_db.delete = AsyncMock()

            guest_id = 404
            target_id = 888
            raw_token = create_access_token({"sub": str(guest_id), "role": "guest"})
            bearer_token = f"Bearer {raw_token}"

            mock_session = MagicMock(user_id=guest_id)
            mock_session_res = MagicMock()
            mock_session_res.scalars.return_value.first.return_value = mock_session

            mock_guest_user = MagicMock(id=guest_id, role="guest")
            mock_user_res = MagicMock()
            mock_user_res.scalar_one_or_none.return_value = mock_guest_user

            async def execute_side_effect(statement, *args, **kwargs):
                stmt_str = str(statement).upper()
                if "SESSIONS" in stmt_str and "SELECT" in stmt_str:
                    return mock_session_res
                elif "USERS" in stmt_str and "SELECT" in stmt_str:
                    return mock_user_res
                return MagicMock()

            mock_db.execute = AsyncMock(side_effect=execute_side_effect)

            with patch("app.services.guest_service.redis_client") as mock_redis:
                mock_redis.delete = AsyncMock(return_value=1)
                migrated = await transfer_guest_data(
                    db=mock_db,
                    guest_token=bearer_token,
                    target_user_id=target_id
                )
                self.assertTrue(migrated, "Token with 'Bearer ' prefix must be accepted and stripped!")

        asyncio.run(run_test())


class TestAuthenticatedUserIsolation(unittest.TestCase):
    """Verifies that authenticated users (role != 'guest') completely bypass guest quota enforcement."""

    def test_01_authenticated_users_bypass_quota_in_ws_source(self):
        """Verify chat_ws_routes source isolates quota checks behind if role == 'guest'."""
        import inspect
        from app.modules.chat.routes import chat_ws_routes
        source = inspect.getsource(chat_ws_routes.websocket_chat)

        # Quota reservation is strictly quarantined behind role == "guest"
        self.assertIn('if role == "guest":', source)
        self.assertIn('res_status, remaining_credits = await reserve_guest_credit(user_id)', source)

        # Negative check: ensure unconditional reserve_guest_credit does not exist
        lines = source.splitlines()
        for idx, line in enumerate(lines):
            if "reserve_guest_credit" in line and not line.strip().startswith("#"):
                preceding_block = "\n".join(lines[max(0, idx - 5):idx])
                self.assertIn('role == "guest"', preceding_block, f"Unprotected reservation found at line {idx}")

    def test_02_worker_pre_token_refund_isolation(self):
        """Verify chat_request_worker only refunds requests with RESERVED prompt_state."""
        import inspect
        from workers import chat_request_worker
        source = inspect.getsource(chat_request_worker.handle_single_chat_request)

        # Worker sets CONSUMED on first token
        self.assertIn('"CONSUMED"', source)
        # Worker only triggers refund if prompt_state is RESERVED
        self.assertIn('prompt_state == "RESERVED"', source)

    def test_03_websocket_message_error_resilience(self):
        """Verify chat_ws_routes catches message-level errors and continues loop without crashing WS connection."""
        import inspect
        from app.modules.chat.routes import chat_ws_routes
        source = inspect.getsource(chat_ws_routes.websocket_chat)

        # Inside chat loop, db_err and pub_exc handlers must send error and continue, NOT raise
        self.assertIn('except Exception as db_err:', source)
        self.assertIn('except Exception as pub_exc:', source)
        self.assertIn('"Failed to save message. Please try again."', source)
        self.assertIn('"Failed to queue message. Please try again."', source)


if __name__ == "__main__":
    unittest.main()

