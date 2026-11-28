import os
import re
import uuid
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant import Assistant
from app.models.assistant_knowledge_base import AssistantKnowledgeBase
from app.models.knowledge_base import KnowledgeBase
from app.models.knowledge_base_document import KnowledgeBaseDocument
from app.modules.assistants.models.assistant_config import AssistantConfig
from app.modules.mini_ai.cache import invalidate_kb_cache
from app.modules.mini_ai.entitlements import get_mini_ai_entitlements
from app.modules.mini_ai.gap_service import list_gaps, resolve_gap
from app.modules.mini_ai.ingestion import (
    extract_text_from_upload,
    index_knowledge_texts,
    parse_qa_pairs,
)
from app.modules.mini_ai.lead_service import list_leads
from app.modules.mini_ai.repository import mini_ai_repository
from app.modules.mini_ai.schemas import (
    ALLOWED_EXTENSIONS,
    MAX_CHUNKS_PER_MINI_AI,
    MAX_FILE_BYTES,
    MAX_MINI_AIS_PER_USER,
    MiniAIDocumentItem,
    MiniAIDocumentsResponse,
    MiniAIGapItem,
    MiniAIInsightsResponse,
    MiniAILeadItem,
    MiniAIResponse,
    MiniAIUpdateRequest,
)

UPLOAD_ROOT = os.path.join("uploads", "mini_ai")


def _safe_filename(filename: str) -> str:
    base = os.path.basename(filename or "knowledge.txt")
    return re.sub(r"[^A-Za-z0-9._-]", "_", base)


def _to_response(
    assistant: Assistant,
    kb_id: int | None,
    chunks_count: int,
) -> MiniAIResponse:
    return MiniAIResponse(
        id=assistant.id,
        name=assistant.name,
        code=assistant.code,
        description=assistant.description,
        system_prompt=assistant.system_prompt,
        is_active=assistant.is_active,
        is_custom=assistant.is_custom,
        owner_user_id=assistant.owner_user_id,
        knowledge_base_id=kb_id,
        chunks_count=chunks_count,
        share_slug=assistant.share_slug,
        is_public=assistant.is_public,
        strict_rag=assistant.strict_rag,
        allowed_domains=assistant.allowed_domains,
        welcome_message=assistant.welcome_message,
        created_at=assistant.created_at,
    )


class MiniAIService:
    async def _prepare_knowledge_inputs(
        self,
        user_id: int,
        qa_pairs_json: str | None,
        upload_file: UploadFile | None,
    ) -> tuple[list[str], str | None, str, bytes, str]:
        qa_blocks = parse_qa_pairs(qa_pairs_json)
        saved_path: str | None = None
        ext = ""
        file_bytes = b""
        safe_name = "inline_qa.txt"
        mime_type = "text/plain"

        if upload_file is not None and upload_file.filename:
            ext = os.path.splitext(upload_file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValueError("Allowed file types: .txt, .csv, .pdf")
            file_bytes = await upload_file.read()
            if len(file_bytes) > MAX_FILE_BYTES:
                raise ValueError("File exceeds maximum size of 5 MB.")
            safe_name = _safe_filename(upload_file.filename)
            mime_type = upload_file.content_type or "application/octet-stream"
            user_dir = os.path.join(UPLOAD_ROOT, str(user_id))
            os.makedirs(user_dir, exist_ok=True)
            saved_path = os.path.join(user_dir, f"{uuid.uuid4().hex}_{safe_name}")
            with open(saved_path, "wb") as f:
                f.write(file_bytes)

        try:
            raw_texts = list(qa_blocks)
            if saved_path:
                extracted = await extract_text_from_upload(saved_path, ext)
                if extracted.strip():
                    raw_texts.append(extracted)
            return raw_texts, saved_path, safe_name, file_bytes, mime_type
        except Exception:
            if saved_path and os.path.exists(saved_path):
                os.remove(saved_path)
            raise

    async def _attach_and_index_knowledge(
        self,
        db: AsyncSession,
        kb_id: int,
        user_id: int,
        raw_texts: list[str],
        saved_path: str | None,
        safe_name: str,
        file_bytes: bytes,
        mime_type: str,
        max_chunks: int = MAX_CHUNKS_PER_MINI_AI,
    ) -> int:
        if not raw_texts:
            return 0
        kbd = KnowledgeBaseDocument(
            knowledge_base_id=kb_id,
            file_name=safe_name,
            file_path=saved_path or "inline_qa",
            mime_type=mime_type,
            file_size=len(file_bytes) if file_bytes else None,
            is_active=True,
            status="completed",
        )
        db.add(kbd)
        await db.flush()
        return await index_knowledge_texts(
            db=db,
            kbd_id=kbd.id,
            source_name=safe_name,
            raw_texts=raw_texts,
            uploaded_by=user_id,
            max_chunks=max_chunks,
        )

    async def create_mini_ai(
        self,
        db: AsyncSession,
        user_id: int,
        name: str,
        system_prompt: str,
        description: str | None = None,
        qa_pairs_json: str | None = None,
        upload_file: UploadFile | None = None,
    ) -> MiniAIResponse:
        cleaned_name = name.strip()
        cleaned_prompt = system_prompt.strip()
        if not cleaned_name or not cleaned_prompt:
            raise ValueError("Name and instructions (system prompt) are required.")
        if await mini_ai_repository.is_reserved_platform_name(db, cleaned_name):
            raise ValueError(
                "This name is reserved by the platform. Please choose a different name."
            )

        entitlements = await get_mini_ai_entitlements(db, user_id)
        current_count = await mini_ai_repository.lock_and_count_user_mini_ais(db, user_id)
        if current_count >= entitlements.max_bots:
            raise ValueError(
                f"Plan limit reached ({entitlements.max_bots} Mini AI max on {entitlements.plan_name} plan). "
                "Upgrade your plan or delete an existing Mini AI."
            )

        raw_texts, saved_path, safe_name, file_bytes, mime_type = (
            await self._prepare_knowledge_inputs(user_id, qa_pairs_json, upload_file)
        )

        try:
            unique_suffix = uuid.uuid4().hex[:8]
            assistant = Assistant(
                name=cleaned_name,
                code=f"mini_{user_id}_{unique_suffix}",
                description=(description or "").strip() or None,
                system_prompt=cleaned_prompt,
                owner_user_id=user_id,
                is_custom=True,
                strict_rag=True,
                is_active=True,
            )
            db.add(assistant)
            await db.flush()

            config = AssistantConfig(
                assistant_id=assistant.id,
                rag_enabled=bool(raw_texts),
                memory_enabled=True,
                cag_enabled=False,
                tool_calling_enabled=False,
                voice_enabled=False,
                ocr_enabled=False,
                web_search_enabled=False,
                document_chat_enabled=False,
                image_generation_enabled=False,
            )
            db.add(config)

            kb = KnowledgeBase(
                name=f"MiniAI KB - {cleaned_name[:120]}",
                code=f"kb_mini_{user_id}_{unique_suffix}",
                description=f"Private knowledge base for user {user_id}",
                is_active=True,
            )
            db.add(kb)
            await db.flush()

            akb = AssistantKnowledgeBase(
                assistant_id=assistant.id,
                knowledge_base_id=kb.id,
                is_active=True,
            )
            db.add(akb)

            chunks_count = await self._attach_and_index_knowledge(
                db=db,
                kb_id=kb.id,
                user_id=user_id,
                raw_texts=raw_texts,
                saved_path=saved_path,
                safe_name=safe_name,
                file_bytes=file_bytes,
                mime_type=mime_type,
                max_chunks=entitlements.max_chunks_per_bot,
            )

            await db.flush()
            await db.refresh(assistant)
            return _to_response(assistant, kb.id, chunks_count)
        except Exception:
            if saved_path and os.path.exists(saved_path):
                os.remove(saved_path)
            raise

    async def add_knowledge(
        self,
        db: AsyncSession,
        mini_ai_id: int,
        user_id: int,
        qa_pairs_json: str | None = None,
        upload_file: UploadFile | None = None,
    ) -> MiniAIResponse:
        assistant = await mini_ai_repository.get_user_mini_ai(db, mini_ai_id, user_id)
        if not assistant:
            raise LookupError("Mini AI not found or access denied.")

        kb_id, existing_chunks = await mini_ai_repository.get_kb_and_chunk_count(
            db, assistant.id
        )
        if kb_id is None:
            raise ValueError("Knowledge base not initialized for this Mini AI.")

        entitlements = await get_mini_ai_entitlements(db, user_id)
        remaining_chunks = entitlements.max_chunks_per_bot - existing_chunks
        if remaining_chunks <= 0:
            raise ValueError(
                f"Chunk limit ({entitlements.max_chunks_per_bot}) reached on your {entitlements.plan_name} plan."
            )

        raw_texts, saved_path, safe_name, file_bytes, mime_type = (
            await self._prepare_knowledge_inputs(user_id, qa_pairs_json, upload_file)
        )
        if not raw_texts:
            if saved_path and os.path.exists(saved_path):
                os.remove(saved_path)
            raise ValueError("Please provide Q&A pairs or a file with text content.")

        try:
            added_chunks = await self._attach_and_index_knowledge(
                db=db,
                kb_id=kb_id,
                user_id=user_id,
                raw_texts=raw_texts,
                saved_path=saved_path,
                safe_name=safe_name,
                file_bytes=file_bytes,
                mime_type=mime_type,
                max_chunks=remaining_chunks,
            )
            if assistant.config is not None and not assistant.config.rag_enabled:
                assistant.config.rag_enabled = True

            await db.flush()
            await invalidate_kb_cache(kb_id)
            return _to_response(assistant, kb_id, existing_chunks + added_chunks)
        except Exception:
            if saved_path and os.path.exists(saved_path):
                os.remove(saved_path)
            raise

    async def list_mini_ais(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[MiniAIResponse]:
        assistants = await mini_ai_repository.list_user_mini_ais(db, user_id)
        responses: list[MiniAIResponse] = []
        for assistant in assistants:
            kb_id, chunks_count = await mini_ai_repository.get_kb_and_chunk_count(
                db, assistant.id
            )
            responses.append(_to_response(assistant, kb_id, chunks_count))
        return responses

    async def update_mini_ai(
        self,
        db: AsyncSession,
        mini_ai_id: int,
        user_id: int,
        payload: MiniAIUpdateRequest,
    ) -> MiniAIResponse:
        assistant = await mini_ai_repository.get_user_mini_ai(db, mini_ai_id, user_id)
        if not assistant:
            raise LookupError("Mini AI not found or access denied.")

        entitlements = await get_mini_ai_entitlements(db, user_id)
        if not entitlements.allow_public_embed and (
            payload.is_public is True
            or payload.share_slug is not None
            or payload.allowed_domains is not None
        ):
            raise PermissionError(
                "Upgrade to a Paid plan to publish share links or embed your Mini AI."
            )

        if payload.share_slug is not None:
            if await mini_ai_repository.is_share_slug_taken(db, payload.share_slug, assistant.id):
                raise ValueError("This share slug is already in use.")
            assistant.share_slug = payload.share_slug
        elif payload.is_public and not assistant.share_slug:
            assistant.share_slug = f"bot-{assistant.id}-{uuid.uuid4().hex[:6]}"

        if payload.name is not None:
            cleaned_update_name = payload.name.strip()
            if await mini_ai_repository.is_reserved_platform_name(db, cleaned_update_name):
                raise ValueError(
                    "This name is reserved by the platform. Please choose a different name."
                )
            assistant.name = cleaned_update_name
        if payload.description is not None:
            assistant.description = payload.description.strip() or None
        if payload.system_prompt is not None:
            assistant.system_prompt = payload.system_prompt.strip()
        if payload.strict_rag is not None:
            assistant.strict_rag = payload.strict_rag
        if payload.is_public is not None:
            assistant.is_public = payload.is_public
        if payload.allowed_domains is not None:
            assistant.allowed_domains = payload.allowed_domains or None
        if payload.welcome_message is not None:
            assistant.welcome_message = payload.welcome_message.strip() or None

        await db.flush()
        await db.refresh(assistant)
        kb_id, chunks_count = await mini_ai_repository.get_kb_and_chunk_count(db, assistant.id)
        return _to_response(assistant, kb_id, chunks_count)

    async def list_documents(
        self,
        db: AsyncSession,
        mini_ai_id: int,
        user_id: int,
    ) -> MiniAIDocumentsResponse:
        assistant = await mini_ai_repository.get_user_mini_ai(db, mini_ai_id, user_id)
        if not assistant:
            raise LookupError("Mini AI not found or access denied.")
        entitlements = await get_mini_ai_entitlements(db, user_id)
        kb_id, chunks_used = await mini_ai_repository.get_kb_and_chunk_count(db, assistant.id)
        if kb_id is None:
            return MiniAIDocumentsResponse(
                documents=[],
                chunks_used=0,
                chunk_limit=entitlements.max_chunks_per_bot,
                remaining_chunks=entitlements.max_chunks_per_bot,
            )
        rows = await mini_ai_repository.list_documents_with_counts(db, kb_id)
        items = [
            MiniAIDocumentItem(
                id=doc.id,
                file_name=doc.file_name,
                mime_type=doc.mime_type,
                status=doc.status,
                error_message=doc.error_message,
                chunk_count=cnt,
                created_at=doc.created_at,
            )
            for doc, cnt in rows
        ]
        return MiniAIDocumentsResponse(
            documents=items,
            chunks_used=chunks_used,
            chunk_limit=entitlements.max_chunks_per_bot,
            remaining_chunks=max(0, entitlements.max_chunks_per_bot - chunks_used),
        )

    async def delete_document(
        self,
        db: AsyncSession,
        mini_ai_id: int,
        doc_id: int,
        user_id: int,
    ) -> None:
        assistant = await mini_ai_repository.get_user_mini_ai(db, mini_ai_id, user_id)
        if not assistant:
            raise LookupError("Mini AI not found or access denied.")
        kb_id, _ = await mini_ai_repository.get_kb_and_chunk_count(db, assistant.id)
        if kb_id is None:
            raise LookupError("Document not found.")

        file_path = await mini_ai_repository.delete_single_document(db, kb_id, doc_id)
        if file_path is None:
            raise LookupError("Document not found.")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        await invalidate_kb_cache(kb_id)

    async def get_insights(
        self,
        db: AsyncSession,
        mini_ai_id: int,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> MiniAIInsightsResponse:
        assistant = await mini_ai_repository.get_user_mini_ai(db, mini_ai_id, user_id)
        if not assistant:
            raise LookupError("Mini AI not found or access denied.")
        entitlements = await get_mini_ai_entitlements(db, user_id)
        if not entitlements.allow_insights:
            raise PermissionError(
                "Upgrade to a Paid plan to unlock Leads & Knowledge Gaps."
            )
        leads, total_leads = await list_leads(db, assistant.id, limit=limit, offset=offset)
        gaps, total_gaps = await list_gaps(db, assistant.id, limit=limit, offset=offset)
        return MiniAIInsightsResponse(
            leads=[MiniAILeadItem.model_validate(l) for l in leads],
            gaps=[MiniAIGapItem.model_validate(g) for g in gaps],
            total_leads=total_leads,
            total_gaps=total_gaps,
        )

    async def train_gap(
        self,
        db: AsyncSession,
        mini_ai_id: int,
        gap_id: int,
        user_id: int,
        answer: str,
    ) -> MiniAIResponse:
        assistant = await mini_ai_repository.get_user_mini_ai(db, mini_ai_id, user_id)
        if not assistant:
            raise LookupError("Mini AI not found or access denied.")
        entitlements = await get_mini_ai_entitlements(db, user_id)
        if not entitlements.allow_insights:
            raise PermissionError(
                "Upgrade to a Paid plan to train Knowledge Gaps."
            )
        gap = await resolve_gap(db, gap_id, assistant.id)
        if not gap:
            raise LookupError("Knowledge gap not found.")

        import json as _json
        qa_payload = _json.dumps([{"question": gap.question, "answer": answer.strip()}])
        return await self.add_knowledge(
            db=db,
            mini_ai_id=mini_ai_id,
            user_id=user_id,
            qa_pairs_json=qa_payload,
        )

    async def delete_mini_ai(
        self,
        db: AsyncSession,
        mini_ai_id: int,
        user_id: int,
    ) -> None:
        assistant = await mini_ai_repository.get_user_mini_ai(db, mini_ai_id, user_id)
        if not assistant:
            raise LookupError("Mini AI not found or access denied.")

        kb_id, _ = await mini_ai_repository.get_kb_and_chunk_count(db, assistant.id)
        file_paths = await mini_ai_repository.delete_user_mini_ai_resources(db, assistant)
        await invalidate_kb_cache(kb_id)
        for path in file_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


mini_ai_service = MiniAIService()
