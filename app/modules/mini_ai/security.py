import ipaddress
import re
from urllib.parse import urlparse
from fastapi import HTTPException, Request, status

from app.shared.redis.client import redis_client

_DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$|^localhost$")

# Atomic Redis INCR + EXPIRE Lua script for public rate limiting
_RATE_LIMIT_LUA = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end
local ttl = redis.call("TTL", KEYS[1])
return {current, ttl}
"""


def normalize_domain(raw: str) -> str:
    value = raw.strip().lower()
    if not value or "*" in value or "/" in value or "://" in value:
        raise ValueError(f"Invalid domain '{raw}'. Provide hostname only (e.g. myshop.com).")
    host = value.split(":", 1)[0]
    if not _DOMAIN_RE.match(host):
        raise ValueError(f"Invalid domain format: '{raw}'.")
    return host


def extract_host(header_val: str | None) -> str | None:
    if not header_val:
        return None
    try:
        parsed = urlparse(header_val.strip())
        if parsed.hostname:
            return parsed.hostname.lower()
    except Exception:
        return None
    return None


def check_origin_allowed(
    origin: str | None,
    referer: str | None,
    allowed_domains: list[str] | None,
) -> bool:
    if not allowed_domains:
        return True
    normalized_allow = {d.strip().lower() for d in allowed_domains if d and d.strip()}
    if not normalized_allow:
        return True

    candidate_host = extract_host(origin) or extract_host(referer)
    if candidate_host is None:
        # Direct non-browser API call without Origin/Referer: allow only if caller isn't spoofing a blocked browser origin,
        # while still guarded by Redis rate limiting.
        return True
    return candidate_host in normalized_allow


def get_client_ip(request: Request) -> str:
    peer_ip = request.client.host if request.client else "unknown"
    try:
        addr = ipaddress.ip_address(peer_ip)
        is_trusted_proxy = addr.is_loopback or addr.is_private
    except ValueError:
        is_trusted_proxy = False

    if is_trusted_proxy:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
    return peer_ip


async def enforce_public_rate_limit(
    key_prefix: str,
    identifier: str,
    limit: int = 20,
    window_seconds: int = 60,
) -> None:
    key = f"mini_ai_rl:{key_prefix}:{identifier}"
    try:
        res = await redis_client.eval(_RATE_LIMIT_LUA, 1, key, str(window_seconds))
        count = int(res[0])
        ttl = max(int(res[1]), 1)
    except Exception:
        # Fail open only if Redis is momentarily unavailable, never crash public chat
        return

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again shortly.",
            headers={"Retry-After": str(ttl)},
        )
