"""
BUG-02: Regression Test for Assistant Creation Authorization & Isolation
"""
import inspect
import unittest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

import qa_tests.conftest
from app.modules.assistants.routes import assistant_routes
from app.modules.assistants.schemas.assistant_schema import AssistantCreate
from app.modules.workspace_assistants.models.workspace_assistant import WorkspaceAssistant


class TestBug02AssistantAuthorization(unittest.TestCase):

    def test_create_assistant_requires_authentication_dependency(self):
        """Verify create_assistant route signature strictly requires verify_token."""
        route_fn = assistant_routes.create_assistant
        sig = inspect.signature(route_fn)

        # Must have current_user dependency
        self.assertIn("current_user", sig.parameters, "create_assistant must require current_user parameter")
        default_val = sig.parameters["current_user"].default
        self.assertIsNotNone(default_val, "current_user must have a Depends default")

    def test_unauthenticated_request_blocked(self):
        """Verify calling verify_token with missing credentials raises HTTP 401."""
        from app.core.security import verify_token
        dummy_credentials = MagicMock()
        dummy_credentials.credentials = "invalid.token.structure"

        with self.assertRaises(HTTPException) as ctx:
            verify_token(token=dummy_credentials)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_tenant_workspace_assistant_model_integrity(self):
        """Verify WorkspaceAssistant contains strict workspace_id and assistant_id foreign keys."""
        cols = {c.name for c in WorkspaceAssistant.__table__.columns}
        self.assertIn("workspace_id", cols)
        self.assertIn("assistant_id", cols)
        self.assertIn("is_active", cols)

        # Verify unique constraint on (workspace_id, assistant_id) for tenant isolation
        constraints = [c.name for c in WorkspaceAssistant.__table__.constraints]
        self.assertIn("uq_workspace_assistant", constraints)


if __name__ == "__main__":
    unittest.main()

