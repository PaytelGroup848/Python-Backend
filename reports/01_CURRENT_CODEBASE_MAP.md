# CURRENT CODEBASE ARCHITECTURE & SYSTEM MAP

**Evaluation Mode:** CTO Forensic Audit & System Architecture Mapping  
**Date:** September 16, 2026  
**Scope:** Full Stack (FastAPI Python Backend + Next.js TypeScript Frontend)  
**Corpus Root:** `c:\Users\Paytel\Downloads\ai-llm\ai-llm` & `c:\Users\Paytel\Downloads\ai-llm\ai-platform-frontend`  

---

## 1. System Entrypoints

### 1.1 Backend Entrypoint (`ai-llm`)
- **Main Application File:** `app/main.py`
- **Application Server:** FastAPI initialized as `app = FastAPI(...)`
- **Startup Lifecycle Hook (`startup_event`):**
  - Fail-fast database connectivity verification via `SELECT 1`.
  - Registration of storage runtime factories (`register_storage_runtime_factories()`).
  - Pipeline executor registration (`register_pipeline_executors()`).
  - Background scheduler initialization (`scheduler.start()`).
  - Redis Pub/Sub response listener (`start_app_pubsub_listener()`) and Stream listener (`start_app_response_listener()`).
- **Shutdown Lifecycle Hook (`shutdown_event`):**
  - Scheduler shutdown (`scheduler.shutdown()`).
  - Background listener cancellation.
- **Port / Host:** Port `8000` (Docker host port mapped `8000:8000`).

### 1.2 Frontend Entrypoint (`ai-platform-frontend`)
- **Framework:** Next.js 14+ App Router (`src/app/`)
- **Root Layout:** `src/app/layout.tsx`
- **Root Page / Landing:** `src/app/page.tsx`
- **State Stores:** Zustand (`src/stores/auth-store.ts`, `src/features/chat/stores/conversation-store.ts`)
- **API Client:** Axios singleton `src/services/api/client.ts` with 401 response interceptor.
- **WebSocket Client:** Singleton `SocketClient` (`src/services/websocket/socket-client.ts`).

---

## 2. Component & Subsystem Maps for Target Bug Scope

### 2.1 WebSocket Chat Streaming
- **Route File:** `app/modules/chat/routes/chat_ws_routes.py` (`@router.websocket("/ws/chat")`)
- **Connection Registry:** `app/shared/websocket/websocket_manager.py` (`WSConnectionManager`)
- **Message Dispatch:** Redis Streams `CHAT_REQUEST_STREAM` via `redis_stream_service.publish()`
- **Worker Execution:** Background workers (`workers/chat_request_worker.py`, `workers/chat_response_worker.py`)
- **Pub/Sub Backchannel:** Channel pattern `ws:req:<request_id>` listened by `start_app_pubsub_listener()` in `app/main.py` and forwarded to registered WebSocket.
- **Frontend Consumer:** `src/features/chat/components/chat-window.tsx` & `src/services/websocket/socket-client.ts`.

### 2.2 Document Upload & Processing
- **Route File:** `app/routes/pdf_routes.py` (`POST /pdf/upload-pdf`, `GET /pdf/job-status/{job_id}`)
- **Models:**
  - `DocumentJob` (`app/models/document_job.py`): tracks `status` ("queued", "processing", "completed", "failed"), `chunks_stored`, `error_message`.
  - `KnowledgeBase` (`app/models/knowledge_base.py`)
  - `KnowledgeBaseDocument` (`app/models/knowledge_base_document.py`)
- **Parser Services:** `app/services/document_parser_service.py` (`parse_document()`), `app/services/file_parser_service.py` (`parse_pdf`, `parse_docx`, etc.).
- **Upload Directory:** `uploads/` (mapped to container root `/app/uploads`).
- **Frontend Component:** `src/features/documents/components/upload-button.tsx`.
- **Frontend Service:** `src/features/documents/services/document-service.ts`.

### 2.3 AI Assistants Subsystem
- **Global Assistant Route:** `app/modules/assistants/routes/assistant_routes.py` (`POST /assistants/`, `GET /assistants/`, `GET /assistants/{assistant_id}`)
- **Global Model:** `app/models/assistant.py` (`Assistant` with `name`, `code`, `description`, `system_prompt`, `is_active`).
- **Workspace Tenant Link:** `app/modules/workspace_assistants/models/workspace_assistant.py` (`WorkspaceAssistant` linking `workspace_id` and `assistant_id` with `uq_workspace_assistant`).
- **Frontend Component:** `src/features/playground/components/assistant-selector.tsx`.
- **Frontend Service:** `src/features/playground/services/assistant-service.ts` (`getAssistants()`).

### 2.4 Public AI API & Developer Keys
- **Public API Route:** `app/modules/public_api/routes/ai_api_routes.py` (`POST /v1/chat/completions`, `GET /v1/models`).
- **API Schema:** `app/modules/public_api/schemas/ai_api_schema.py` (`ChatCompletionRequest`, `ChatMessage`, `ChatCompletionResponse`).
- **API Key Route:** `app/modules/api_keys/routes/api_key_routes.py` (`POST /api-keys`, `GET /api-keys`, `GET /api-keys/usage`, `PATCH /api-keys/{id}/disable`, `DELETE /api-keys/{id}`).
- **API Key Auth Dependency:** `app/modules/api_keys/dependencies/api_key_auth.py` (`validate_api_key`).
- **API Key Auth Service:** `app/modules/api_keys/services/api_key_auth_service.py` (SHA-256 hash lookup in `api_keys` table).
- **Frontend Component:** `src/features/chat/components/api-keys-modal.tsx`.
- **Frontend Service:** `src/features/chat/services/api-key-service.ts`.

### 2.5 Security & Authentication Boundaries
- **JWT Helper:** `app/core/security.py` (`create_access_token`, `create_refresh_token`, `verify_token`, `get_current_user`, `require_role`).
- **Token Claims:** `sub` (User ID), `role` (Role), `exp` (Expiry).
- **Algorithm:** `HS256` signed with `SECRET_KEY`.

---

## 3. Build & Test Tooling Discovered

### 3.1 Backend Tooling (`ai-llm`)
- **Python Version:** 3.11 (Docker container) / 3.13 (Host environment).
- **Compiler:** `python -m py_compile <files>`
- **Test Framework:** `unittest` / `pytest`
- **Master Test Runner:** `python -m qa_tests.run_all_qa_tests`

### 3.2 Frontend Tooling (`ai-platform-frontend`)
- **Package Manager:** `npm`
- **Scripts in `package.json`:**
  - `npm run dev` (starts Next.js dev server)
  - `npm run build` (Next.js production build with TypeScript check and page compilation)
  - `npm run start` (starts Next.js production server)
  - `npm run lint` (ESLint static analysis)
