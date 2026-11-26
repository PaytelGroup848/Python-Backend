"""
app/modules/finance/market_cache.py
Enterprise Redis Market Micro-Cache Layer
Manages smart, market-aware TTL caching for sub-10ms quote response latency.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.db.redis_client import redis_client
from app.modules.finance.schemas import StockQuote, MarketStatus

logger = logging.getLogger("market_cache")

# IST timezone definition (UTC + 05:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Local in-memory fallback cache: key -> (serialized_quote, expire_epoch)
_LOCAL_MEMORY_CACHE: dict[str, tuple[str, float]] = {}


class MarketCache:
    """
    Tiered caching system (Redis primary + Local Memory fail-safe).
    Automatically adapts TTL based on Indian stock exchange trading windows.
    """

    CACHE_PREFIX = "market:quote:"

    @classmethod
    def get_ist_now(cls) -> datetime:
        """Returns current wall-clock time in Indian Standard Time (IST)."""
        return datetime.now(timezone.utc).astimezone(IST)

    @classmethod
    def compute_market_status_and_ttl(cls, exchange: str = "NSE") -> tuple[MarketStatus, int]:
        """
        Calculates whether the exchange is currently active and assigns optimal TTL.
        NSE / BSE Trading Hours: Mon-Fri 09:15 to 15:30 IST.
        """
        now_ist = cls.get_ist_now()
        weekday = now_ist.weekday() # 0 = Monday, 6 = Sunday

        # Weekend: Market Closed
        if weekday in (5, 6): # Saturday or Sunday
            return MarketStatus.CLOSED, 43200 # 12 hours TTL

        hour = now_ist.hour
        minute = now_ist.minute
        time_minutes = hour * 60 + minute

        # Pre-market session: 09:00 - 09:15 IST
        if 9 * 60 <= time_minutes < 9 * 60 + 15:
            return MarketStatus.PRE_MARKET, 30 # 30s TTL

        # Regular Trading Session: 09:15 - 15:30 IST
        if 9 * 60 + 15 <= time_minutes <= 15 * 60 + 30:
            return MarketStatus.OPEN, 25 # 25s TTL during live trading

        # Post-market hours (15:31 onwards or before 09:00 on weekdays)
        return MarketStatus.CLOSED, 900 # 15 minutes TTL

    @classmethod
    async def get_cached_quote(cls, symbol: str) -> Optional[StockQuote]:
        """
        Fetches normalized quote from Redis (or local in-memory fallback).
        """
        cache_key = f"{cls.CACHE_PREFIX}{symbol.upper()}"
        try:
            # 1. Primary: Redis Lookup
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                parsed = json.loads(cached_data)
                return StockQuote(**parsed)
        except Exception as exc:
            logger.debug(f"Redis cache lookup failed for {symbol}: {exc}")

        # 2. Secondary: In-Memory L1 Cache Check
        now_epoch = datetime.now(timezone.utc).timestamp()
        if cache_key in _LOCAL_MEMORY_CACHE:
            raw_str, expire_epoch = _LOCAL_MEMORY_CACHE[cache_key]
            if now_epoch < expire_epoch:
                try:
                    return StockQuote(**json.loads(raw_str))
                except Exception:
                    pass
            else:
                _LOCAL_MEMORY_CACHE.pop(cache_key, None)

        return None

    @classmethod
    async def set_cached_quote(cls, quote: StockQuote, ttl_seconds: Optional[int] = None) -> None:
        """
        Stores quote in Redis and local memory with market-aware TTL.
        """
        cache_key = f"{cls.CACHE_PREFIX}{quote.symbol.upper()}"
        if ttl_seconds is None:
            _, ttl_seconds = cls.compute_market_status_and_ttl(quote.exchange)

        json_payload = quote.model_dump_json()

        # 1. Set in Redis
        try:
            await redis_client.set(cache_key, json_payload, ex=ttl_seconds)
        except Exception as exc:
            logger.debug(f"Redis cache set failed for {quote.symbol}: {exc}")

        # 2. Set in Local Memory Fallback
        now_epoch = datetime.now(timezone.utc).timestamp()
        _LOCAL_MEMORY_CACHE[cache_key] = (json_payload, now_epoch + ttl_seconds)


market_cache = MarketCache()
