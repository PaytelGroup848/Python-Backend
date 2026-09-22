import asyncio
import logging
from fastapi import APIRouter, Response, status
from sqlalchemy import text
from app.db.database import AsyncSessionLocal
from app.db.redis_client import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_probe():
    """
    Liveness probe: verifies the FastAPI application process is alive and able to handle HTTP events.
    Does NOT depend on external infrastructure to prevent cascading crash loops.
    """
    return {"status": "alive"}


@router.get("/ready")
async def readiness_probe(response: Response):
    """
    Readiness probe: verifies external infrastructure dependencies (PostgreSQL & Redis).
    Returns HTTP 200 when all dependencies are healthy.
    Returns HTTP 503 Service Unavailable with Retry-After header when degraded.
    """
    checks = {
        "database": "unknown",
        "redis": "unknown"
    }

    # 1. Probe PostgreSQL with a strict 3-second timeout
    try:
        async with asyncio.timeout(3.0):
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as db_err:
        logger.warning(f"Readiness probe DB check failed: {db_err}")
        checks["database"] = f"error: {str(db_err)}"

    # 2. Probe Redis with a strict 3-second timeout
    try:
        async with asyncio.timeout(3.0):
            await redis_client.ping()
        checks["redis"] = "ok"
    except Exception as redis_err:
        logger.warning(f"Readiness probe Redis check failed: {redis_err}")
        checks["redis"] = f"error: {str(redis_err)}"

    # 3. Aggregate health verdict
    is_ready = checks["database"] == "ok" and checks["redis"] == "ok"

    if is_ready:
        response.status_code = status.HTTP_200_OK
        return {
            "status": "ready",
            "dependencies": checks
        }
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        response.headers["Retry-After"] = "5"
        return {
            "status": "degraded",
            "dependencies": checks
        }
