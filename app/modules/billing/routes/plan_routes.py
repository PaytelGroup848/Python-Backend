import json
import logging
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError

from app.db.database import get_db
from app.core.config import settings
from app.shared.redis.client import redis_client
from app.modules.billing.models.plan import Plan
from app.modules.billing.models.plan_version import PlanVersion
from app.modules.billing.models.plan_price import PlanPrice
from app.modules.billing.models.subscription import Subscription

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/plans",
    tags=["Plans"]
)

PUBLIC_PLANS_CACHE_KEY = "billing:public_plans"
CACHE_TTL_SECONDS = 600  # 10 minutes


def _extract_optional_user_id(request: Request) -> Optional[int]:
    """Safely extracts authenticated user_id from Authorization header if present, without failing for guests."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        sub = payload.get("sub")
        return int(sub) if sub is not None else None
    except Exception:
        return None


@router.get("")
async def get_public_plans(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Public Read-Only Catalog of Subscription Plans.
    
    Architecture:
    1. Static plan catalog is cached in Redis (target p95 < 20ms for cache hits).
    2. If user is authenticated, their active plan ('is_current') is overlaid in-memory.
    3. Strictly READ-ONLY: Never seeds or mutates the database on a GET request.
    """
    cached_data = None
    try:
        raw_cache = await redis_client.get(PUBLIC_PLANS_CACHE_KEY)
        if raw_cache:
            cached_data = json.loads(raw_cache)
    except Exception as e:
        logger.warning(f"[PLANS_ROUTE] Redis cache read failed: {e}")

    if not cached_data:
        # Query active public plans
        plan_stmt = (
            select(Plan)
            .where(Plan.is_public == True, Plan.is_active == True)
            .order_by(Plan.id.asc())
        )
        plan_res = await db.execute(plan_stmt)
        plans = plan_res.scalars().all()

        catalog = []
        for plan in plans:
            # Query active version
            ver_stmt = (
                select(PlanVersion)
                .where(PlanVersion.plan_id == plan.id, PlanVersion.is_active == True)
                .order_by(PlanVersion.version_number.desc())
            )
            ver_res = await db.execute(ver_stmt)
            version = ver_res.scalars().first()

            prices_list = []
            if version:
                price_stmt = (
                    select(PlanPrice)
                    .where(PlanPrice.plan_version_id == version.id, PlanPrice.is_active == True)
                )
                price_res = await db.execute(price_stmt)
                prices = price_res.scalars().all()
                for p in prices:
                    prices_list.append({
                        "id": p.id,
                        "billing_cycle": p.billing_cycle,
                        "amount": float(p.amount),
                        "currency": p.currency,
                        "provider": p.provider
                    })

            # Feature descriptions based on tier
            features = []
            if plan.plan_code == "free":
                features = [
                    f"{version.monthly_token_limit if version else 20000:,} monthly tokens",
                    "Access to base AI models",
                    "Standard response latency",
                    "Community support"
                ]
            elif plan.plan_code == "pro":
                features = [
                    f"{version.monthly_token_limit if version else 1000000:,} monthly tokens",
                    "Access to Claude 3.5, GPT-4o & frontier models",
                    "Priority generation & zero queue waiting",
                    "Developer API Keys & Agent tool calling",
                    "Priority 24/7 technical support"
                ]
            elif plan.plan_code == "enterprise":
                features = [
                    f"{version.monthly_token_limit if version else 5000000:,} monthly tokens",
                    "Custom fine-tuned models & dedicated capacity",
                    "Highest concurrency & rate limits",
                    "Custom knowledge corpora & pipeline integration",
                    "Dedicated SLA & enterprise compliance"
                ]
            else:
                features = [
                    f"{version.monthly_token_limit if version else 0:,} monthly tokens",
                    f"{version.monthly_request_limit if version else 0:,} monthly requests",
                    "Standard AI features"
                ]

            catalog.append({
                "id": plan.id,
                "plan_code": plan.plan_code,
                "plan_name": plan.plan_name,
                "description": plan.description,
                "monthly_token_limit": version.monthly_token_limit if version else 0,
                "monthly_request_limit": version.monthly_request_limit if version else 0,
                "features": features,
                "prices": prices_list
            })

        cached_data = catalog

        # Save to Redis cache
        try:
            await redis_client.set(
                PUBLIC_PLANS_CACHE_KEY,
                json.dumps(cached_data),
                ex=CACHE_TTL_SECONDS
            )
        except Exception as e:
            logger.warning(f"[PLANS_ROUTE] Redis cache write failed: {e}")

    # In-memory overlay for authenticated user (never mutates public Redis cache)
    user_id = _extract_optional_user_id(request)
    active_plan_code = "free"
    active_billing_cycle = "monthly"
    if user_id:
        sub_stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id, Subscription.status == "active")
        )
        sub_res = await db.execute(sub_stmt)
        active_sub = sub_res.scalars().first()
        if active_sub:
            active_plan_code = active_sub.plan_name
            if active_sub.start_date and active_sub.end_date:
                diff_days = (active_sub.end_date - active_sub.start_date).days
                if diff_days > 60:
                    active_billing_cycle = "yearly"

    response_plans = []
    for p in cached_data:
        p_copy = dict(p)
        p_copy["is_current"] = (p_copy["plan_code"].lower() == active_plan_code.lower())
        response_plans.append(p_copy)

    return {
        "plans": response_plans,
        "active_plan_code": active_plan_code,
        "active_billing_cycle": active_billing_cycle
    }

