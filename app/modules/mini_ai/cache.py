import logging
from app.shared.redis.client import redis_client

logger = logging.getLogger(__name__)


async def get_kb_cache_version(knowledge_base_ids: list[int]) -> str:
    if not knowledge_base_ids:
        return "0"
    try:
        keys = [f"kb_cache_ver:{kb_id}" for kb_id in sorted(set(knowledge_base_ids))]
        vals = await redis_client.mget(*keys)
        return "-".join(str(v or "0") for v in vals)
    except Exception as exc:
        logger.warning("KB cache version lookup failed: %s", exc)
        return "0"


async def invalidate_kb_cache(knowledge_base_id: int | None) -> None:
    if knowledge_base_id is None:
        return
    try:
        await redis_client.incr(f"kb_cache_ver:{knowledge_base_id}")
    except Exception as exc:
        logger.warning("KB cache invalidation failed for kb=%s: %s", knowledge_base_id, exc)
