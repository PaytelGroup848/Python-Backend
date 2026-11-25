import logging
from typing import Optional, Tuple
from starlette.requests import Request
import httpx

logger = logging.getLogger(__name__)

# In-memory cache for IP lookups to eliminate redundant external calls
_GEOIP_CACHE: dict[str, Tuple[Optional[str], Optional[str]]] = {}


def get_client_ip(request: Optional[Request]) -> str:
    if not request:
        return ""
    # 1. Cloudflare connecting IP
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    # 2. X-Forwarded-For (client is first in list)
    x_forwarded = request.headers.get("x-forwarded-for")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    # 3. X-Real-IP
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()
    # 4. Direct socket host
    if request.client is not None:
        host = getattr(request.client, "host", None)
        if host:
            return str(host).strip()
    return ""


async def resolve_geoip(
    request: Optional[Request] = None,
    ip_override: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Production Fail-Safe GeoIP Resolver.
    Returns: (city, country_code) e.g. ("Patna", "IN").
    
    Guarantees:
    - Never raises an unhandled exception.
    - Zero latency if behind Cloudflare edge (reads CF-IPCity and CF-IPCountry).
    - Internal timeout guard (max 1.5s) with fallback to (None, None).
    """
    try:
        # Step 1: Check Cloudflare edge headers (instant 0ms resolution)
        if request:
            cf_country = request.headers.get("cf-ipcountry")
            cf_city = request.headers.get("cf-ipcity")
            if cf_country and cf_country != "XX":
                return (cf_city.strip() if cf_city else None, cf_country.strip().upper())

        # Step 2: Determine IP
        ip = ip_override or (get_client_ip(request) if request else "")
        if not ip:
            return None, None

        # Step 3: Local / internal networks
        if ip in ("127.0.0.1", "::1", "localhost") or ip.startswith(("192.168.", "10.", "172.16.")):
            return "Local", "IN"

        # Step 4: Check cache
        if ip in _GEOIP_CACHE:
            return _GEOIP_CACHE[ip]

        # Step 5: Fast external GeoIP lookup with timeout
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode,city")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    city = data.get("city")
                    country = data.get("countryCode")
                    result = (city, country)
                    if len(_GEOIP_CACHE) < 5000:
                        _GEOIP_CACHE[ip] = result
                    return result

    except Exception as e:
        logger.debug(f"GeoIP resolution gracefully bypassed: {e}")

    return None, None
