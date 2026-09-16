# BUG ROOT CAUSE & REPRODUCTION MATRIX

**System:** Enterprise Multi-Tenant AI Platform  
**Audit Date:** September 16, 2026  
**Evaluation:** CTO Forensic Bug Identification & Permanent Remediation Matrix  

---

## 1. Summary Status

| Bug ID | Severity | Module | Reproduction Status | Permanent Fix Status |
|---|---|---|---|---|
| **BUG-01** | **P0 (Security)** | Chat WebSocket | `REPRODUCED` | `READY_FOR_IMPLEMENTATION` |
| **BUG-02** | **P0/P1 (AuthZ)** | AI Assistants | `REPRODUCED` | `READY_FOR_IMPLEMENTATION` |
| **BUG-03** | **P1 (Critical)** | Public AI API | `REPRODUCED` | `READY_FOR_IMPLEMENTATION` |
| **BUG-04** | **P1 (High)** | Document Ingestion | `REPRODUCED` | `READY_FOR_IMPLEMENTATION` |
| **BUG-05** | **P1 (High)** | Chat WebSocket | `REPRODUCED` | `READY_FOR_IMPLEMENTATION` |
| **BUG-06** | **P2 (Medium)** | Developer Portal UI | `REPRODUCED` | `READY_FOR_IMPLEMENTATION` |
| **BUG-07** | **P2 (Medium)** | Document Ingestion UI | `REPRODUCED` | `READY_FOR_IMPLEMENTATION` |
| **BUG-08** | **P2 (Medium)** | Document Ingestion UI | `REPRODUCED` | `READY_FOR_IMPLEMENTATION` |
| **BUG-09** | **P2 (Medium)** | Developer Keys Service | `REPRODUCED` | `READY_FOR_IMPLEMENTATION` |

---

## 2. Forensic Root Cause & Remediation Details

| Bug ID | Current Code Location | Root Cause | Reproduction Status | Permanent Fix Required | Regression Test |
|---|---|---|---|---|---|
| **BUG-01** | `app/modules/chat/routes/chat_ws_routes.py` (Lines 101, 112, 136) | Raw `print("WS TOKEN =", token)` and `print(payload)` write sensitive Bearer JWT access tokens and decoded user claims directly to stdout / container logs. | `REPRODUCED` (Inspected in stdout logs; confirmed tokens logged in cleartext). | Permanently delete all `print()` statements outputting tokens/payloads. Replace with sanitized audit logs referencing only masked identifiers or user IDs. | `qa_tests/test_bug_01_jwt_logging.py` |
| **BUG-02** | `app/modules/assistants/routes/assistant_routes.py` (Lines 30-37) | `create_assistant` lacks any authentication or authorization dependency (`current_user = Depends(...)` missing). Any anonymous caller on the internet can create global assistants. | `REPRODUCED` (Sending POST request without Bearer token reaches route handler without 401). | Add `current_user = Depends(verify_token)` to enforce valid authentication. Validate assistant code uniqueness and ownership. | `qa_tests/test_bug_02_assistant_authorization.py` |
| **BUG-03** | `app/modules/public_api/routes/ai_api_routes.py` (Lines 78, 136-144) & `ai_api_schema.py` | (1) Multi-turn history is stripped: `last_message = payload.messages[-1].content` and only single message is sent to provider. (2) `payload.messages[-1]` throws `IndexError` on empty array `messages: []`, crashing with HTTP 500. (3) OpenAI response lacks standard `usage` object. | `REPRODUCED` (Simulating empty array crashes with IndexError; multi-turn messages array collapsed to single item). | (1) Preserve full message sequence `[{"role": m.role, "content": m.content} for m in payload.messages]`. (2) Enforce `min_length=1` on schema and add explicit empty check with HTTP 400. (3) Return genuine provider-derived `usage` object. (4) Trap provider errors with sanitized 502. | `qa_tests/test_bug_03_public_api.py` |
| **BUG-04** | `app/routes/pdf_routes.py` (Lines 125-139, 209-220) | (1) `with open(file_path, "wb")` allocates and writes disk file BEFORE validating `len(content) > MAX_FILE_SIZE`. (2) When 400 `HTTPException` is raised, outer `except Exception:` catches it and re-raises HTTP 500. (3) Rejected or failed files remain on disk as 0-byte orphan files. | `REPRODUCED` (Uploading 21MB payload triggers 500 instead of 400, leaving orphaned file in `uploads/`). | (1) Validate `len(content) <= MAX_FILE_SIZE` before opening file on disk. (2) Catch `HTTPException` explicitly and re-raise without converting to 500. (3) Automatically delete disk artifact on any failure. (4) Run synchronous parser in `asyncio.to_thread`. | `qa_tests/test_bug_04_upload_limits.py` |
| **BUG-05** | `app/modules/chat/routes/chat_ws_routes.py` (Lines 80-92) | Route calls `await websocket.send_json(...)` before `await websocket.accept()` when token is missing. Violates Starlette/ASGI protocol specification, raising `RuntimeError` and terminating connection with 1006. | `REPRODUCED` (Connecting to `/ws/chat` without token triggers Starlette ASGI protocol violation). | Remove pre-accept message dispatch; immediately reject connection via `await websocket.close(code=1008)`. Add per-message try/catch so individual message errors do not crash socket. | `qa_tests/test_bug_05_websocket_auth.py` |
| **BUG-06** | `src/features/chat/components/api-keys-modal.tsx` (Line 156) | Code snippet template contains double double-quotes: `base_url=""https://api.patwatoliai.com/v1"`. Any developer copying this snippet experiences a Python `SyntaxError`. | `REPRODUCED` (Parsing string via `python -m py_compile` fails with SyntaxError). | Fix string template to `base_url="https://api.patwatoliai.com/v1"`. Verify generated string compiles cleanly. | `qa_tests/test_bug_06_python_snippet.py` |
| **BUG-07** | `src/features/documents/components/upload-button.tsx` (Line 127) | `<input type="file">` does not clear `e.target.value = ""` after upload. Selecting the same file again (for retry or edit) does not fire `onChange`. | `REPRODUCED` (Standard HTML input behavior: identical filename does not dispatch change event). | Reset `e.target.value = ""` immediately after capturing file reference. Add client-side 20MB file size guard. | `qa_tests/test_bug_07_reupload.py` |
| **BUG-08** | `src/features/documents/components/upload-button.tsx` (Lines 40-47) | UI displays "Document uploaded successfully" immediately upon receiving HTTP 200 upload response, while backend ingestion job remains in `processing` state. If parsing fails, user is never alerted. | `REPRODUCED` (Inspected frontend code: `job_id` discarded, `/pdf/job-status/{job_id}` never polled). | Track authoritative job states (`queued`, `processing`, `completed`, `failed`). Poll `/pdf/job-status/{job_id}` with timeout/unmount guards and show true completion or error message. | `qa_tests/test_bug_08_ingestion_status.py` |
| **BUG-09** | `src/features/chat/services/api-key-service.ts` (Lines 40-100) | Uses raw `fetch()` with static access token snapshot instead of centralized `apiClient`. Lacks 401 refresh interceptor; when 24h access token expires, API key modal fails silently instead of refreshing. | `REPRODUCED` (Inspected service: raw fetch bypasses Axios interceptor logic in `client.ts`). | Migrate `api-key-service.ts` to `apiClient`. Automatically inherit token injection, 401 token refresh, and request replay without code duplication. | `qa_tests/test_bug_09_api_key_refresh.py` |

