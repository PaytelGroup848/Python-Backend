from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assistant import Assistant
from app.models.assistant_knowledge_base import AssistantKnowledgeBase
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.models.knowledge_base_document import KnowledgeBaseDocument
from app.models.user import User


class MiniAIRepository:
    async def lock_and_count_user_mini_ais(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> int:
        # Row-level lock serializes concurrent creates by the same user (prevents multi-tab quota bypass).
        await db.execute(
            select(User.id).where(User.id == user_id).with_for_update()
        )
        result = await db.execute(
            select(func.count(Assistant.id)).where(
                Assistant.owner_user_id == user_id,
                Assistant.is_custom.is_(True),
                Assistant.is_active.is_(True),
            )
        )
        return int(result.scalar() or 0)

    async def list_user_mini_ais(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[Assistant]:
        result = await db.execute(
            select(Assistant)
            .options(selectinload(Assistant.config))
            .where(
                Assistant.owner_user_id == user_id,
                Assistant.is_custom.is_(True),
                Assistant.is_active.is_(True),
            )
            .order_by(Assistant.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_mini_ai(
        self,
        db: AsyncSession,
        mini_ai_id: int,
        user_id: int,
    ) -> Assistant | None:
        result = await db.execute(
            select(Assistant)
            .options(selectinload(Assistant.config))
            .where(
                Assistant.id == mini_ai_id,
                Assistant.owner_user_id == user_id,
                Assistant.is_custom.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_kb_and_chunk_count(
        self,
        db: AsyncSession,
        assistant_id: int,
    ) -> tuple[int | None, int]:
        akb_res = await db.execute(
            select(AssistantKnowledgeBase.knowledge_base_id).where(
                AssistantKnowledgeBase.assistant_id == assistant_id
            )
        )
        kb_id = akb_res.scalar_one_or_none()
        if kb_id is None:
            return None, 0

        cnt_res = await db.execute(
            select(func.count(Document.id))
            .join(
                KnowledgeBaseDocument,
                Document.knowledge_base_document_id == KnowledgeBaseDocument.id,
            )
            .where(KnowledgeBaseDocument.knowledge_base_id == kb_id)
        )
        return kb_id, int(cnt_res.scalar() or 0)

    async def delete_user_mini_ai_resources(
        self,
        db: AsyncSession,
        assistant: Assistant,
    ) -> list[str]:
        akb_res = await db.execute(
            select(AssistantKnowledgeBase.knowledge_base_id).where(
                AssistantKnowledgeBase.assistant_id == assistant.id
            )
        )
        kb_ids = [row for row in akb_res.scalars().all()]
        file_paths: list[str] = []

        if kb_ids:
            kbd_res = await db.execute(
                select(KnowledgeBaseDocument.id, KnowledgeBaseDocument.file_path).where(
                    KnowledgeBaseDocument.knowledge_base_id.in_(kb_ids)
                )
            )
            kbd_rows = kbd_res.all()
            kbd_ids = [r[0] for r in kbd_rows]
            file_paths = [r[1] for r in kbd_rows if r[1] and r[1] != "inline_qa"]

            if kbd_ids:
                await db.execute(
                    delete(Document).where(Document.knowledge_base_document_id.in_(kbd_ids))
                )
                await db.execute(
                    delete(KnowledgeBaseDocument).where(KnowledgeBaseDocument.id.in_(kbd_ids))
                )

            await db.execute(
                delete(AssistantKnowledgeBase).where(
                    AssistantKnowledgeBase.assistant_id == assistant.id
                )
            )
            await db.execute(delete(KnowledgeBase).where(KnowledgeBase.id.in_(kb_ids)))

        await db.delete(assistant)
        await db.flush()
        return file_paths

    async def get_public_by_slug(
        self,
        db: AsyncSession,
        share_slug: str,
    ) -> Assistant | None:
        result = await db.execute(
            select(Assistant)
            .options(selectinload(Assistant.config))
            .where(
                Assistant.share_slug == share_slug,
                Assistant.is_public.is_(True),
                Assistant.is_active.is_(True),
                Assistant.is_custom.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def is_share_slug_taken(
        self,
        db: AsyncSession,
        share_slug: str,
        exclude_assistant_id: int,
    ) -> bool:
        res = await db.execute(
            select(Assistant.id).where(
                Assistant.share_slug == share_slug,
                Assistant.id != exclude_assistant_id,
            )
        )
        return res.scalar_one_or_none() is not None

    async def list_documents_with_counts(
        self,
        db: AsyncSession,
        kb_id: int,
    ) -> list[tuple[KnowledgeBaseDocument, int]]:
        res = await db.execute(
            select(KnowledgeBaseDocument, func.count(Document.id))
            .outerjoin(Document, Document.knowledge_base_document_id == KnowledgeBaseDocument.id)
            .where(KnowledgeBaseDocument.knowledge_base_id == kb_id)
            .group_by(KnowledgeBaseDocument.id)
            .order_by(KnowledgeBaseDocument.created_at.desc())
        )
        return [(row[0], int(row[1] or 0)) for row in res.all()]

    async def delete_single_document(
        self,
        db: AsyncSession,
        kb_id: int,
        doc_id: int,
    ) -> str | None:
        res = await db.execute(
            select(KnowledgeBaseDocument).where(
                KnowledgeBaseDocument.id == doc_id,
                KnowledgeBaseDocument.knowledge_base_id == kb_id,
            )
        )
        kbd = res.scalar_one_or_none()
        if kbd is None:
            return None

        file_path = kbd.file_path
        await db.execute(
            delete(Document).where(Document.knowledge_base_document_id == doc_id)
        )
        await db.execute(
            delete(KnowledgeBaseDocument).where(
                KnowledgeBaseDocument.id == doc_id,
                KnowledgeBaseDocument.knowledge_base_id == kb_id,
            )
        )
        await db.flush()
        return file_path if file_path and file_path != "inline_qa" else ""


    async def is_reserved_platform_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> bool:
        normalized = name.strip().lower()
        if normalized in {"general chat", "patwatoli ai", "patwatoli", "assistant"}:
            return True
        res = await db.execute(
            select(Assistant.id).where(
                Assistant.owner_user_id.is_(None),
                func.lower(Assistant.name) == normalized,
            )
        )
        return res.scalar_one_or_none() is not None

    async def get_custom_kb_inventory(
        self,
        db: AsyncSession,
        assistant_id: int,
    ) -> str:
        res = await db.execute(
            select(Assistant.is_custom).where(Assistant.id == assistant_id)
        )
        if not res.scalar_one_or_none():
            return ""

        kb_id, total_chunks = await self.get_kb_and_chunk_count(db, assistant_id)
        if kb_id is None:
            return ""

        docs = await self.list_documents_with_counts(db, kb_id)
        if not docs:
            return "=== MY MINI AI KNOWLEDGE INVENTORY ===\nNo files or Q&A uploaded yet.\n=== END OF INVENTORY ==="

        doc_list = ", ".join(f"{doc.file_name} ({cnt} chunks)" for doc, cnt in docs)
        sample_res = await db.execute(
            select(Document.content)
            .join(
                KnowledgeBaseDocument,
                Document.knowledge_base_document_id == KnowledgeBaseDocument.id,
            )
            .where(KnowledgeBaseDocument.knowledge_base_id == kb_id)
            .order_by(Document.id.asc())
            .limit(2)
        )
        samples = [s[:300] for s in sample_res.scalars().all() if s]
        preview = "\n".join(samples)
        return (
            "=== MY MINI AI KNOWLEDGE INVENTORY ===\n"
            f"Uploaded datasets/files: {doc_list}\n"
            f"Total indexed chunks: {total_chunks}\n"
            + (f"Sample content preview:\n{preview}\n" if preview else "")
            + "=== END OF INVENTORY ==="
        )


mini_ai_repository = MiniAIRepository()
