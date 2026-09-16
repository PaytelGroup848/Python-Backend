# 02 — Comprehensive QA Test Matrix

## Test Categories & Severity Definitions
- **P0 (Blocker/Outage):** Service crash, authentication outage, silent corruption, credential leakage.
- **P1 (Critical):** Core auth flow broken, token refresh failure, improper session persistence, contract violation.
- **P2 (Major):** Performance degradation, failure-handling gap, observability issue, session bloat.
- **P3 (Minor):** Cosmetic response inconsistency, non-breaking validation gap.

---

| TEST-ID | Category | Component | Source File | Endpoint / Function | Preconditions | Test Steps | Expected Result | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AUTH-01** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/login` | Active user in DB | Submit correct email & password | HTTP 200, valid access_token, refresh_token, session in DB | P0 |
| **AUTH-02** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/login` | Active user in DB | Submit wrong password | HTTP 401 "Invalid credentials", failed attempt recorded | P1 |
| **AUTH-03** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/login` | User not in DB | Submit non-existent email | HTTP 401 "Invalid credentials", no stack trace | P1 |
| **AUTH-04** | Authentication | AuthService | `app/modules/auth/services/auth_service.py` | `verify_password` | User with malformed hash | Submit login for user with plain text / malformed hash | Returns False, yields HTTP 401, NO HTTP 500 | P0 |
| **AUTH-05** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/login` | Valid service | Submit empty email or empty password | HTTP 422 Unprocessable Entity, validation details | P2 |
| **AUTH-06** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/login` | Valid service | Submit invalid email format ("notanemail") | HTTP 422 Unprocessable Entity | P2 |
| **AUTH-07** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/login` | Valid service | Submit 10,000 character string in email/password | HTTP 422 or 400, no memory exhaustion or crash | P2 |
| **AUTH-08** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/login` | Valid service | Submit non-ASCII Unicode (e.g. Emoji / Cyrillic) in password | Correct UTF-8 handling, no encoding crash | P2 |
| **AUTH-09** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/login` | 5 failed attempts in Redis | Attempt 6th login with correct credentials | HTTP 403 "Too many failed attempts" | P1 |
| **AUTH-10** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/google` | Valid Google ID token | Submit GoogleAuthRequest with mocked claims | HTTP 200, user auto-provisioned, tokens returned | P1 |
| **AUTH-11** | Authentication | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/google` | Spoofed token | Submit token with untrusted issuer / audience | HTTP 401 "Invalid Google token", attempt recorded | P0 |
| **TOK-01** | Token Lifecycle | SecurityCore | `app/core/security.py` | `create_access_token` | Active secret key | Generate token and inspect claims | Contains `sub`, `role`, `exp` = 1440m (24h) | P1 |
| **TOK-02** | Token Lifecycle | SecurityCore | `app/core/security.py` | `create_refresh_token` | Active secret key | Generate token and inspect claims | Contains `sub`, `role`, `exp` = 7 days | P1 |
| **TOK-03** | Token Lifecycle | SecurityCore | `app/core/security.py` | `verify_token` | Expired token | Verify token with `exp` in the past | HTTP 401 "Invalid or expired token" | P1 |
| **TOK-04** | Token Lifecycle | SecurityCore | `app/core/security.py` | `verify_token` | Altered signature | Tamper with token payload / signature | HTTP 401 "Invalid or expired token" | P0 |
| **REF-01** | Refresh Contract | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/refresh` | Valid refresh token | Send `{ "refresh_token": "..." }` in JSON body | HTTP 200, new access_token issued | P0 |
| **REF-02** | Refresh Contract | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/refresh` | Valid refresh token | Send `?refresh_token=...` as URL query parameter | HTTP 200, new access_token issued (backward compat) | P1 |
| **REF-03** | Refresh Contract | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/refresh` | Missing token | Send empty body and no query param | HTTP 422 "refresh_token is required" | P2 |
| **REF-04** | Refresh Contract | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/refresh` | Revoked token | Send refresh token after session deleted in DB | HTTP 401 "Invalid refresh token" | P1 |
| **REF-05** | Refresh Contract | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/refresh` | Expired token | Send refresh token older than 7 days | HTTP 401 "Expired or invalid refresh token" | P1 |
| **REF-06** | Concurrency / Race | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/refresh` | Valid refresh token | Fire 10 simultaneous refresh requests with same token | All requests succeed or handle safely without DB lockup | P1 |
| **LOG-01** | Logout | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/logout` | Active session in DB | Send `{ "refresh_token": "..." }` in JSON body | HTTP 200, session removed from DB table | P1 |
| **LOG-02** | Logout | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/logout` | Active session in DB | Send `?refresh_token=...` as URL query param | HTTP 200, session removed from DB table | P1 |
| **LOG-03** | Logout | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/logout` | No active session | Send logout without token | HTTP 200 {"message": "Logged out successfully"} | P2 |
| **LOG-04** | Logout Multi-Device| AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/logout` | Session A & B active | Logout Session A | Session A revoked; Session B remains valid | P0 |
| **LOG-05** | Quota Protection | AuthRouter | `app/modules/auth/routes/auth_routes.py` | `POST /auth/logout` | User with tokens in `usage:{id}` | Logout user | `usage:{id}` is NOT deleted in Redis | P0 |
| **SESS-01**| Session Cleanup | CleanupJob | `app/jobs/session_cleanup_job.py` | `cleanup_expired_sessions` | Stale session (> 8 days) | Run cleanup job | Stale session purged; sessions < 8 days retained | P2 |
| **SESS-02**| Session Cleanup | Scheduler | `app/jobs/scheduler.py` | APScheduler | App startup | Start scheduler | Job registered for daily 03:00 UTC execution | P2 |
| **DB-01** | DB Reliability | MainBoot | `app/main.py` | `startup_event` | Correct credentials | Application boots | `SELECT 1` passes, Uvicorn starts listening | P0 |
| **DB-02** | DB Reliability | MainBoot | `app/main.py` | `startup_event` | Invalid credentials | Application boots | Startup fails fast, Uvicorn terminates (no zombie) | P0 |
| **DB-03** | DB Keepalive | Database | `app/db/database.py` | `create_async_engine` | PostgreSQL 15 | Check connect_args | `tcp_keepalives_idle=60`, interval=10, count=5 | P1 |
| **DB-04** | Pool Recovery | Database | `app/db/database.py` | `get_db` | Stale connection | Pool checkout | `pool_pre_ping=True` detects dead socket and refreshes | P1 |
| **RED-01** | Redis Resilience | SecurityService | `app/services/security_service.py` | `is_locked` | Redis offline | Check lockout | Emits SECURITY ALERT warning, fails open (login works) | P0 |
| **RED-02** | Redis Resilience | SecurityService | `app/services/security_service.py` | `record_failed_attempt`| Redis offline | Record failure | Catches exception, logs warning, does not crash | P1 |
| **RED-03** | Redis Recovery | SecurityService | `app/services/security_service.py` | `is_locked` | Redis restored | Attempt login | Normal rate limiting automatically resumes | P1 |
| **DOCK-01**| Docker Health | DockerCompose | `docker-compose.yml` | `postgres.healthcheck` | Correct password | Check `docker ps` | Container reports `(healthy)` | P0 |
| **DOCK-02**| Docker Health | DockerCompose | `docker-compose.yml` | `postgres.healthcheck` | Invalid password | Injected invalid pass | Container reports `(unhealthy)`, app does not start | P0 |
| **FE-01** | Frontend Interceptor| ApiClient | `src/services/api/client.ts` | Axios Response Hook | 401 on protected route | Trigger 401 | Sends `{ refresh_token }` to `/auth/refresh`, retries | P1 |
| **FE-02** | Frontend Logout | AuthStore | `src/stores/auth-store.ts` | `useAuthStore.logout` | Authenticated store | Trigger logout() | Awaits backend revocation, clears local storage in finally | P1 |
| **FE-03** | Frontend Resilience | AuthStore | `src/stores/auth-store.ts` | `useAuthStore.logout` | Backend down | Trigger logout() | Logs safe warning (no token leak), clears local state | P1 |
| **SEC-01** | Security Leakage | Global | All auth endpoints | Logs & Responses | Execute auth flows | Verify no passwords, hashes, or tokens in logs | P0 |

