import io
import json
import uuid
import pytest
from fastapi import UploadFile
from sqlalchemy import select

from app.db.database import AsyncSessionLocal, engine
from app.models.user import User
from app.modules.assistants.repositories.assistant_repository import assistant_repository
from app.modules.assistants.services.assistant_runtime_service import assistant_runtime_service
from app.modules.mini_ai.service import mini_ai_service


@pytest.mark.asyncio
async def test_mini_ai_strict_cross_tenant_isolation():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User.id).order_by(User.id.asc()).limit(2))
        user_ids = list(res.scalars().all())
        if len(user_ids) < 2:
            pytest.skip("Need at least 2 users in DB to verify cross-tenant isolation")

        user_a, user_b = user_ids[0], user_ids[1]
        bot_name = f"QA_MiniAI_{uuid.uuid4().hex[:6]}"

        csv_upload = UploadFile(
            filename="shop_faq.csv",
            file=io.BytesIO(b"question,answer\nHours?,9am to 9pm\nDelivery?,Free above 500\n"),
        )

        created = await mini_ai_service.create_mini_ai(
            db=db,
            user_id=user_a,
            name=bot_name,
            system_prompt="Answer strictly from shop rules.",
            qa_pairs_json=json.dumps([{"question": "Return policy?", "answer": "7 days"}]),
            upload_file=csv_upload,
        )
        assert created.owner_user_id == user_a
        assert created.is_custom is True
        assert created.chunks_count >= 1

        # 1. Listing isolation
        list_a = [a.id for a in await assistant_repository.list_active(db, user_id=user_a)]
        list_b = [a.id for a in await assistant_repository.list_active(db, user_id=user_b)]
        list_guest = [a.id for a in await assistant_repository.list_active(db, user_id=None)]
        assert created.id in list_a
        assert created.id not in list_b
        assert created.id not in list_guest

        # 2. Runtime execution isolation
        with pytest.raises(PermissionError):
            await assistant_runtime_service.load_runtime(db, created.id, user_id=user_b)

        runtime_a = await assistant_runtime_service.load_runtime(db, created.id, user_id=user_a)
        assert runtime_a.knowledge_base_ids == [created.knowledge_base_id]

        # 3. Append knowledge isolation + chunk count increase
        with pytest.raises(LookupError):
            await mini_ai_service.add_knowledge(
                db=db,
                mini_ai_id=created.id,
                user_id=user_b,
                qa_pairs_json=json.dumps([{"question": "Secret?", "answer": "Hacked"}]),
            )

        appended = await mini_ai_service.add_knowledge(
            db=db,
            mini_ai_id=created.id,
            user_id=user_a,
            qa_pairs_json=json.dumps([{"question": "Warranty?", "answer": "1 year"}]),
        )
        assert appended.chunks_count > created.chunks_count

        # 4. Delete isolation + cleanup
        with pytest.raises(LookupError):
            await mini_ai_service.delete_mini_ai(db, created.id, user_id=user_b)

        await mini_ai_service.delete_mini_ai(db, created.id, user_id=user_a)
        await db.rollback()
    await engine.dispose()
