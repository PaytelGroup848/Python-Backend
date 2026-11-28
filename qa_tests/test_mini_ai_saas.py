import json
import uuid
import pytest
from fastapi import HTTPException
from sqlalchemy import select, text

from app.db.database import AsyncSessionLocal, engine
from app.models.user import User
from app.modules.mini_ai.cache import get_kb_cache_version
from app.modules.mini_ai.gap_service import record_gap
from app.modules.mini_ai.lead_service import capture_lead
from app.modules.mini_ai.repository import mini_ai_repository
from app.modules.mini_ai.schemas import MiniAIUpdateRequest
from app.modules.mini_ai.security import check_origin_allowed, enforce_public_rate_limit
from app.modules.mini_ai.service import mini_ai_service
from app.modules.usage.services.usage_limit_service import usage_limit_service
from app.services.vector_service import semantic_search


@pytest.mark.asyncio
async def test_mini_ai_saas_end_to_end(monkeypatch):
    async with AsyncSessionLocal() as db:
        # 1. Verify tsvector GIN index exists
        idx_res = await db.execute(
            text("SELECT indexname FROM pg_indexes WHERE tablename = 'documents' AND indexname = 'ix_documents_content_tsv'")
        )
        assert idx_res.scalar_one_or_none() == "ix_documents_content_tsv"

        res = await db.execute(select(User.id).order_by(User.id.asc()).limit(2))
        user_ids = list(res.scalars().all())
        if len(user_ids) < 2:
            pytest.skip("Need at least 2 users in DB")
        user_a, user_b = user_ids[0], user_ids[1]

        # 1b. Reserved platform name guard
        with pytest.raises(ValueError):
            await mini_ai_service.create_mini_ai(
                db=db, user_id=user_a, name="General Chat", system_prompt="Test"
            )

        slug = f"shop-{uuid.uuid4().hex[:8]}"
        created = await mini_ai_service.create_mini_ai(
            db=db,
            user_id=user_a,
            name="SaaS Shop Bot",
            system_prompt="Secret instructions here.",
            qa_pairs_json=json.dumps([
                {"question": "Price of SKU-9981X?", "answer": "SKU-9981X costs ₹1,499 with 1 year warranty."}
            ]),
        )
        kb_id = created.knowledge_base_id
        assert kb_id is not None
        assert created.strict_rag is True

        # Verify Mini-AI-only KB inventory works for custom bot and returns empty for platform bot
        inv = await mini_ai_repository.get_custom_kb_inventory(db, created.id)
        assert "inline_qa.txt" in inv
        assert await mini_ai_repository.get_custom_kb_inventory(db, 1) == ""

        # 2. Private bot not exposed publicly
        assert await mini_ai_repository.get_public_by_slug(db, slug) is None

        # 3. Hybrid BM25 + Vector RRF exact SKU retrieval
        hits = await semantic_search(
            db=db,
            query="SKU-9981X",
            knowledge_base_ids=[kb_id],
            user_department="personal",
            user_role="employee",
            limit=5,
        )
        assert any("SKU-9981X" in str(getattr(h, "content", "") or h.get("content", "")) for h in hits)

        # 4. Freemium check: Free user cannot publish/embed or view insights; Paid user can
        async def _free_plan(db, uid):
            return "free"

        monkeypatch.setattr(usage_limit_service, "get_user_plan", _free_plan)
        with pytest.raises(PermissionError):
            await mini_ai_service.update_mini_ai(
                db=db,
                mini_ai_id=created.id,
                user_id=user_a,
                payload=MiniAIUpdateRequest(is_public=True, share_slug=slug),
            )
        with pytest.raises(PermissionError):
            await mini_ai_service.get_insights(db, created.id, user_id=user_a)

        async def _paid_plan(db, uid):
            return "pro"

        monkeypatch.setattr(usage_limit_service, "get_user_plan", _paid_plan)

        # Studio update + public slug + domain allowlist (Paid)
        updated = await mini_ai_service.update_mini_ai(
            db=db,
            mini_ai_id=created.id,
            user_id=user_a,
            payload=MiniAIUpdateRequest(
                is_public=True,
                strict_rag=True,
                share_slug=slug,
                allowed_domains=["myshop.com", "www.myshop.com"],
                welcome_message="Welcome!",
            ),
        )
        assert updated.is_public is True
        assert updated.strict_rag is True
        assert await mini_ai_repository.get_public_by_slug(db, slug) is not None

        # 5. Cross-tenant IDOR checks
        with pytest.raises(LookupError):
            await mini_ai_service.list_documents(db, created.id, user_id=user_b)
        with pytest.raises(LookupError):
            await mini_ai_service.get_insights(db, created.id, user_id=user_b)
        with pytest.raises(LookupError):
            await mini_ai_service.update_mini_ai(
                db, created.id, user_id=user_b, payload=MiniAIUpdateRequest(name="Hacked")
            )

        # 6. Atomic gap deduplication + train gap + lead capture
        await record_gap(db, created.id, "Do you ship to Patna?")
        await record_gap(db, created.id, "do you ship to patna")
        await capture_lead(db, created.id, user_a, "Amit", "+91-9999999999", "Shipping?")
        insights = await mini_ai_service.get_insights(db, created.id, user_id=user_a)
        assert insights.total_leads == 1
        assert insights.total_gaps == 1
        assert insights.gaps[0].hit_count == 2

        trained = await mini_ai_service.train_gap(
            db, created.id, insights.gaps[0].id, user_id=user_a, answer="Yes, 2-day delivery in Patna."
        )
        assert trained.chunks_count > created.chunks_count

        # 7. Document list & delete quota reclaim + cache invalidation
        ver_before = await get_kb_cache_version([kb_id])
        docs_res = await mini_ai_service.list_documents(db, created.id, user_id=user_a)
        assert docs_res.chunks_used == trained.chunks_count
        await mini_ai_service.delete_document(db, created.id, docs_res.documents[0].id, user_id=user_a)
        docs_after = await mini_ai_service.list_documents(db, created.id, user_id=user_a)
        assert docs_after.chunks_used < docs_res.chunks_used
        ver_after = await get_kb_cache_version([kb_id])
        assert ver_after != ver_before

        # 8. Origin allowlist + Redis rate limit 429 check
        assert check_origin_allowed("https://myshop.com", None, ["myshop.com"]) is True
        assert check_origin_allowed("https://evil.com", None, ["myshop.com"]) is False
        rl_id = f"qa_rl_{uuid.uuid4().hex[:8]}"
        await enforce_public_rate_limit("test", rl_id, limit=2, window_seconds=30)
        await enforce_public_rate_limit("test", rl_id, limit=2, window_seconds=30)
        with pytest.raises(HTTPException) as exc_info:
            await enforce_public_rate_limit("test", rl_id, limit=2, window_seconds=30)
        assert exc_info.value.status_code == 429

        # Cleanup
        await mini_ai_service.delete_mini_ai(db, created.id, user_id=user_a)
        await db.rollback()
    await engine.dispose()
