# My Mini AI — Mandatory Codebase Audit Report

## 1. Existing Architecture
- **Backend:** FastAPI async service (`app/main.py`) with modular feature packages under `app/modules/*` (`assistants`, `mini_ai`, `chat`, `provider_runtime`, `retrieval_runtime`, `usage`) and Redis-stream workers (`workers/chat_request_worker.py`).
- **Database:** PostgreSQL 15 (`pgvector/pgvector:pg15`) accessed via SQLAlchemy 2.0 `AsyncSessionLocal` (`app/db/database.py`) and Alembic migrations (`alembic/versions/`, current head `c3d4e5f6a7b8`).
- **Cache & Rate Limiting:** Redis 7 (`app/shared/redis/client.py`, `app/shared/cache/cache_service.py`).
- **Frontend:** Next.js `16.4.3` (App Router, React 18, Tailwind v4, Zustand, React Query, Axios `apiClient` in `src/services/api/client.ts`).

## 2. Existing Database Schema (Relevant Tables)
- `assistants` (`app/models/assistant.py`): `id`, `name`, `code` (unique), `description`, `system_prompt`, `owner_user_id` (FK `users.id` ON DELETE CASCADE), `is_custom`, `is_active`, `created_at`, `updated_at`.
- `assistant_configs` (`app/modules/assistants/models/assistant_config.py`): `rag_enabled`, `memory_enabled`, `web_search_enabled`, etc.
- `knowledge_bases`, `assistant_knowledge_bases`, `knowledge_base_documents`, `documents` (`Vector(384)`, `content`, `source_file`, `page_number`, `department`, `knowledge_base_document_id`).

## 3. Existing Assistant & Document Relationships
- `Assistant` (1) <-> `AssistantKnowledgeBase` <-> `KnowledgeBase` (1) -> `KnowledgeBaseDocument` (N) -> `Document` (N chunks with 384-dim `all-MiniLM-L6-v2` embeddings).

## 4. Existing API Endpoints
- `GET /assistants/`, `GET /assistants/{assistant_id}` (`app/modules/assistants/routes/assistant_routes.py`)
- `POST /mini-ai/`, `GET /mini-ai/`, `POST /mini-ai/{mini_ai_id}/knowledge`, `DELETE /mini-ai/{mini_ai_id}` (`app/modules/mini_ai/routes.py`)
- `WebSocket /ws/chat` (`app/modules/chat/routes/chat_ws_routes.py`), `POST /agent-chat`, `POST /agent-chat/stream` (`app/routes/chat_routes.py`)

## 5. Existing Frontend Components
- `src/features/playground/components/chat-header.tsx`: Assistant dropdown + `+ Create My Mini AI` modal trigger.
- `src/features/mini-ai/components/create-mini-ai-modal.tsx`: Quick create/append/delete modal.
- `src/features/mini-ai/services/mini-ai-service.ts` & `src/features/mini-ai/types/mini-ai.types.ts`.

## 6. Existing Reusable Services
- `app/services/file_parser_service.py`: Already provides `parse_pdf`, `parse_txt`, `parse_csv`, `parse_docx`, `parse_xlsx`.
- `app/modules/retrieval_runtime/services/chunking_service.py`: `chunk_text` (500 chars / 100 overlap).
- `app/modules/retrieval_runtime/services/embedding_service.py`: Singleton `get_embedding_model()` (`all-MiniLM-L6-v2`).
- `app/services/vector_service.py`: `store_document` and `semantic_search`.
- `app/modules/provider_runtime/manager/provider_runtime_manager.py`: Multi-provider LLM cascade (`generate_response`).

## 7. Missing Functionality
1. Studio management APIs (`PATCH /mini-ai/{id}`, `GET /mini-ai/{id}/documents`, `DELETE /mini-ai/{id}/documents/{doc_id}`, `GET /mini-ai/{id}/insights`, gap resolution).
2. Hybrid RAG (`tsvector` + GIN + Reciprocal Rank Fusion) replacing `ILIKE` in `vector_service.py` + versioned KB cache invalidation.
3. `.docx` / `.xlsx` ingestion + contextual `Source:` chunk prefix.
4. Public shareable bot API (`/public/bots/{slug}`, `/chat`, `/leads`), strict RAG + `mini_ai_gaps` atomic deduplication, domain allowlist, Redis rate limiting (`20 req/min/IP`), and `GET /public/widget.js`.
5. Dedicated Next.js Studio page (`/mini-ai`) & Public Bot page (`/b/[slug]`).

## 8. Security Risks & Mitigations
- **Cross-tenant IDOR:** Every Studio query joins/filters `owner_user_id == current_user.id`.
- **Prompt leakage:** Public endpoints never return `system_prompt`, `owner_user_id`, or private config.
- **CORS vs Allowlist:** Public widget routes allow browser preflight while enforcing `Origin`/`Referer` allowlist + atomic Redis rate limiting (defense against header spoofing).
- **Prompt injection:** Retrieved chunks wrapped as untrusted data blocks with explicit system grounding rules.

## 9. Potential Breaking Changes & Guards
- `semantic_search()` in `app/services/vector_service.py` is shared by platform bots (`LawGPT`, `MedAssist AI`): preserve exact function signature and return shape (`id`, `content`, `source_file`, `page_number`, `distance`).
- `documents.content_tsv` generated column must be marked `Computed(..., persisted=True)` in `Document` model so SQLAlchemy `INSERT` does not fail.

## 10. Files to Modify
- `app/models/assistant.py`, `app/models/document.py`, `app/main.py`
- `app/services/vector_service.py`
- `app/modules/mini_ai/*` (`schemas.py`, `repository.py`, `ingestion.py`, `service.py`, `routes.py`)
- `PatwatoliAi-Frontend/src/features/playground/components/chat-header.tsx`
- `PatwatoliAi-Frontend/src/features/mini-ai/*`

## 11. New Files Required
- `alembic/versions/d4e5f6a7b8c9_mini_ai_saas_studio_and_hybrid_rag.py`
- `app/modules/mini_ai/models.py`, `cache.py`, `security.py`, `lead_service.py`, `gap_service.py`, `public_routes.py`
- `PatwatoliAi-Frontend/src/app/mini-ai/page.tsx` + Studio tab components
- `PatwatoliAi-Frontend/src/app/b/[slug]/page.tsx`
- `qa_tests/test_mini_ai_saas.py`

## 12. Migration Strategy
- Chain `d4e5f6a7b8c9` onto `c3d4e5f6a7b8` with full `upgrade()` and `downgrade()`.
- Existing assistants default to `is_public=false`, `strict_rag=false`, `share_slug=NULL`.
- `content_tsv` generated `STORED` column backfills existing `documents` automatically without touching content.

## 13. Implementation Sequence
1. Phase 1: Models + Alembic `d4e5f6a7b8c9` + `upgrade head`
2. Phase 2–4: Cache versioning, Hybrid BM25+Vector RRF, `.docx`/`.xlsx` + contextual chunking
3. Phase 5: Studio management endpoints (`PATCH`, `documents`, `insights`, gap resolution)
4. Phase 6–7: Public routes, Strict RAG, Leads/Gaps services, Redis rate limiter, `widget.js`
5. Phase 8: Next.js `/mini-ai` Studio, `/b/[slug]` public page, dropdown link
6. Phase 9–11: Automated `pytest`, `tsc --noEmit`, `npm run build`
