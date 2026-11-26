"""
app/modules/finance/market_engine.py
Enterprise Live Market Data Provider
Integrates real-time market data providers with async thread-pooling and defensive parsing.
"""

import asyncio
import logging
from typing import Any, Optional
import yfinance as yf

from app.modules.finance.schemas import StockQuote, AssetType, MarketStatus
from app.modules.finance.market_cache import market_cache

logger = logging.getLogger("market_engine")


def format_market_cap_inr(mcap: Optional[float]) -> Optional[str]:
    """
    Formats large integer market capitalizations into clean Indian financial notations (Lakh Cr / Cr).
    """
    if not mcap or mcap <= 0:
        return None
    # 1 Lakh Crore = 10^12
    if mcap >= 1e12:
        lakh_cr = mcap / 1e12
        return f"₹{lakh_cr:.2f} Lakh Cr"
    # 1 Crore = 10^7
    if mcap >= 1e7:
        cr = mcap / 1e7
        return f"₹{cr:.2f} Cr"
    return f"₹{mcap:,.0f}"


def format_market_cap_usd(mcap: Optional[float]) -> Optional[str]:
    """
    Formats US market capitalizations (Trillions / Billions).
    """
    if not mcap or mcap <= 0:
        return None
    if mcap >= 1e12:
        return f"${mcap / 1e12:.2f}T"
    if mcap >= 1e9:
        return f"${mcap / 1e9:.2f}B"
    if mcap >= 1e6:
        return f"${mcap / 1e6:.2f}M"
    return f"${mcap:,.0f}"


class MarketEngine:
    """
    Non-blocking, fault-tolerant financial quote extractor.
    """

    TIMEOUT_SECONDS = 3.0

    @classmethod
    def _fetch_sync(
        cls,
        symbol: str,
        display_name: str,
        exchange: str,
        currency: str,
        asset_type: AssetType
    ) -> Optional[StockQuote]:
        """
        Synchronous worker function executed inside an isolated thread pool.
        """
        try:
            ticker = yf.Ticker(symbol)
            # Use fast_info when available for lowest latency
            fast = getattr(ticker, "fast_info", None)
            info = {}

            # Attempt fast_info extraction
            last_price: Optional[float] = None
            prev_close: Optional[float] = None
            open_price: Optional[float] = None
            day_high: Optional[float] = None
            day_low: Optional[float] = None
            volume: Optional[int] = None
            fifty_two_high: Optional[float] = None
            fifty_two_low: Optional[float] = None
            market_cap: Optional[float] = None

            if fast:
                try:
                    last_price = getattr(fast, "last_price", None)
                    prev_close = getattr(fast, "previous_close", None)
                    open_price = getattr(fast, "open", None)
                    day_high = getattr(fast, "day_high", None)
                    day_low = getattr(fast, "day_low", None)
                    volume = getattr(fast, "last_volume", None)
                    fifty_two_high = getattr(fast, "year_high", None)
                    fifty_two_low = getattr(fast, "year_low", None)
                    market_cap = getattr(fast, "market_cap", None)
                except Exception:
                    pass

            # Fallback to standard info dict if fast_info incomplete
            if last_price is None or prev_close is None:
                try:
                    info = ticker.info or {}
                    last_price = (
                        last_price
                        or info.get("currentPrice")
                        or info.get("regularMarketPrice")
                        or info.get("ask")
                        or info.get("bid")
                        or info.get("previousClose")
                    )
                    prev_close = prev_close or info.get("regularMarketPreviousClose") or info.get("previousClose")
                    open_price = open_price or info.get("regularMarketOpen") or info.get("open")
                    day_high = day_high or info.get("regularMarketDayHigh") or info.get("dayHigh")
                    day_low = day_low or info.get("regularMarketDayLow") or info.get("dayLow")
                    volume = volume or info.get("regularMarketVolume") or info.get("volume")
                    fifty_two_high = fifty_two_high or info.get("fiftyTwoWeekHigh")
                    fifty_two_low = fifty_two_low or info.get("fiftyTwoWeekLow")
                    market_cap = market_cap or info.get("marketCap")
                except Exception:
                    pass

            # Final fallback: 5-day history
            if last_price is None:
                try:
                    hist = ticker.history(period="5d")
                    if not hist.empty:
                        last_price = float(hist["Close"].iloc[-1])
                        if len(hist) > 1:
                            prev_close = float(hist["Close"].iloc[-2])
                        day_high = float(hist["High"].iloc[-1])
                        day_low = float(hist["Low"].iloc[-1])
                        open_price = float(hist["Open"].iloc[-1])
                        volume = int(hist["Volume"].iloc[-1])
                except Exception:
                    pass

            if last_price is None:
                logger.warning(f"Could not resolve price for symbol {symbol}")
                return None

            # Calculate Deltas
            prev_close_val = prev_close if prev_close else last_price
            change = round(last_price - prev_close_val, 2)
            percent_change = round((change / prev_close_val) * 100, 2) if prev_close_val > 0 else 0.0
            is_pos = change >= 0

            # Market status & IST timestamp
            market_status, _ = market_cache.compute_market_status_and_ttl(exchange)
            now_ist_str = market_cache.get_ist_now().strftime("%Y-%m-%d %H:%M:%S IST")

            # Format Market Cap
            mcap_formatted = None
            if market_cap:
                mcap_formatted = (
                    format_market_cap_inr(market_cap)
                    if currency == "INR"
                    else format_market_cap_usd(market_cap)
                )

            pe_ratio = info.get("trailingPE") if info else None

            # Legal company name fallback
            company_title = (info.get("shortName") or info.get("longName")) if info else None
            resolved_name = company_title or display_name

            return StockQuote(
                symbol=symbol,
                name=resolved_name,
                exchange=exchange,
                currency=currency,
                asset_type=asset_type,
                current_price=round(float(last_price), 2),
                previous_close=round(float(prev_close), 2) if prev_close else None,
                open_price=round(float(open_price), 2) if open_price else None,
                day_high=round(float(day_high), 2) if day_high else None,
                day_low=round(float(day_low), 2) if day_low else None,
                change=change,
                percent_change=percent_change,
                is_positive=is_pos,
                volume=int(volume) if volume else None,
                fifty_two_week_high=round(float(fifty_two_high), 2) if fifty_two_high else None,
                fifty_two_week_low=round(float(fifty_two_low), 2) if fifty_two_low else None,
                pe_ratio=round(float(pe_ratio), 2) if pe_ratio else None,
                market_cap=float(market_cap) if market_cap else None,
                market_cap_formatted=mcap_formatted,
                market_status=market_status,
                timestamp_ist=now_ist_str,
                is_stale=False,
            )

        except Exception as exc:
            logger.error(f"Error fetching live quote for {symbol}: {exc}")
            return None

    @classmethod
    async def get_quote(
        cls,
        symbol: str,
        display_name: str,
        exchange: str,
        currency: str,
        asset_type: AssetType
    ) -> Optional[StockQuote]:
        """
        Asynchronously fetches a normalized market quote with Redis caching and a strict timeout guard.
        """
        # 1. Check Cache
        cached = await market_cache.get_cached_quote(symbol)
        if cached:
            return cached

        # 2. Fetch Live Quote in Worker Thread with Timeout Guard
        try:
            quote = await asyncio.wait_for(
                asyncio.to_thread(
                    cls._fetch_sync,
                    symbol,
                    display_name,
                    exchange,
                    currency,
                    asset_type
                ),
                timeout=cls.TIMEOUT_SECONDS
            )
            if quote:
                # Store in Cache
                await market_cache.set_cached_quote(quote)
                return quote
        except asyncio.TimeoutError:
            logger.warning(f"Market data fetch timed out after {cls.TIMEOUT_SECONDS}s for {symbol}")
        except Exception as exc:
            logger.error(f"Unexpected error in MarketEngine for {symbol}: {exc}")

        return None


market_engine = MarketEngine()
