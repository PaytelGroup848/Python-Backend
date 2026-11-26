"""
app/modules/finance/finance_service.py
Enterprise Financial Intelligence Facade
Orchestrates entity resolution, live pricing, and Silicon Valley direct-response formatting.
"""

import re
import logging
from typing import Optional

from app.modules.finance.schemas import StockQuote, MarketStatus
from app.modules.finance.ticker_resolver import ticker_resolver
from app.modules.finance.market_engine import market_engine

logger = logging.getLogger("finance_service")


class FinanceService:
    """
    Unified public facade for all financial and equity market capabilities.
    """

    FINANCE_INTENT_PATTERNS = [
        r"\b(share|stock|equity|scrip|shares|stocks)\s+(price|rate|quote|target|analysis|pe|valuation|market\s+cap)\b",
        r"\b(price|rate|quote)\s+(of|for)\s+([a-zA-Z0-9\s]{2,25})\s+(share|stock)\b",
        r"\b(what\s+is|what's|how\s+is|how\s+much\s+is)\b.{0,30}\b(share\s+price|stock\s+price|market\s+price|target\s+price)\b",
        r"\b(nifty|nifty\s*50|sensex|bank\s*nifty|banknifty|dow\s+jones|nasdaq|sp500|s&p\s*500)\b",
        r"\b(all\s+time\s+high|52\s+week\s+high|52\s+week\s+low|pe\s+ratio|dividend\s+yield)\b",
        r"\b(reliance|tcs|infosys|hdfc|icici|tata\s+motors|zomato|paytm|swiggy|irfc|suzlon|adani)\s+(share|stock|price|rate|today)\b",
        r"\b(bitcoin|ethereum|crypto|btc|eth|solana)\s+(price|rate|today|quote)\b",
        r"\b(gold\s+rate|gold\s+price|silver\s+rate|silver\s+price|crude\s+oil)\b"
    ]

    @classmethod
    def is_finance_query(cls, query: str) -> bool:
        """
        Determines whether the user's natural language prompt is requesting financial market data.
        """
        if not query or not isinstance(query, str):
            return False
        clean_q = query.strip().lower()

        # Check explicit patterns
        for pattern in cls.FINANCE_INTENT_PATTERNS:
            if re.search(pattern, clean_q):
                return True

        # Check if query contains any known ticker entity directly
        resolved = ticker_resolver.resolve_from_query(clean_q)
        if resolved is not None:
            # If query is short or specifically asks about the entity
            terms = ["price", "rate", "kya", "chal", "aaj", "stock", "share", "kitna", "value", "target", "quote", "high", "low"]
            if any(t in clean_q for t in terms) or len(clean_q.split()) <= 4:
                return True

        return False

    @classmethod
    async def resolve_and_fetch_quote(cls, query: str) -> Optional[StockQuote]:
        """
        Resolves entity from natural language and fetches normalized real-time quote.
        """
        resolution = ticker_resolver.resolve_from_query(query, allow_live_search=True)
        if not resolution:
            return None

        symbol, display_name, exchange, currency, asset_type = resolution
        return await market_engine.get_quote(
            symbol=symbol,
            display_name=display_name,
            exchange=exchange,
            currency=currency,
            asset_type=asset_type
        )

    @classmethod
    def format_market_context_card(cls, quote: StockQuote) -> str:
        """
        Formats normalized quote into a structured, Silicon Valley grade verified prompt context.
        """
        curr_sym = "₹" if quote.currency == "INR" else "$"
        arrow = "▲" if quote.is_positive else "▼"
        sign = "+" if quote.is_positive else ""

        status_text = (
            "Live Session (Trading Active)"
            if quote.market_status == MarketStatus.OPEN
            else f"Market Closed (Last Price Recorded)"
        )

        lines = [
            "=== REAL-TIME VERIFIED FINANCIAL MARKET DATA (SOURCE OF TRUTH) ===",
            f"Asset Name: {quote.name}",
            f"Ticker Symbol: {quote.symbol} ({quote.exchange})",
            f"Asset Category: {quote.asset_type.value}",
            f"Current Market Price (LTP): {curr_sym}{quote.current_price:,.2f}",
            f"Day Change: {arrow} {sign}{quote.change:,.2f} ({sign}{quote.percent_change:.2f}%)",
            f"Day Range (Low - High): {curr_sym}{quote.day_low:,.2f} - {curr_sym}{quote.day_high:,.2f}" if quote.day_low and quote.day_high else "",
            f"52-Week Range: {curr_sym}{quote.fifty_two_week_low:,.2f} - {curr_sym}{quote.fifty_two_week_high:,.2f}" if quote.fifty_two_week_low and quote.fifty_two_week_high else "",
            f"Market Capitalization: {quote.market_cap_formatted}" if quote.market_cap_formatted else "",
            f"Price-to-Earnings (P/E): {quote.pe_ratio:.2f}" if quote.pe_ratio else "",
            f"Market Session Status: {status_text}",
            f"Data Timestamp: {quote.timestamp_ist}",
            "=== END OF MARKET DATA ===",
            "",
            "STRICT RESPONSE MANDATE:",
            "1. You MUST provide the exact price, day change, and metrics above DIRECTLY in the response using a clean visual markdown table.",
            "2. NEVER redirect the user to check external links, websites (e.g. NSE, BSE, Moneycontrol), or brokers. The data provided above is verified and current.",
            "3. Always append this subtle statutory educational disclaimer at the very end of your response:",
            "   '*Disclaimer: Market data is provided for educational and informational purposes only. Not financial or investment advice.*'"
        ]

        return "\n".join([line for line in lines if line is not None])

    @classmethod
    async def get_market_context(cls, query: str) -> Optional[str]:
        """
        High-level facade: Resolves, fetches, and returns structured prompt context in one call.
        """
        try:
            quote = await cls.resolve_and_fetch_quote(query)
            if quote:
                return cls.format_market_context_card(quote)
        except Exception as exc:
            logger.error(f"Error resolving market context for '{query}': {exc}")
        return None


finance_service = FinanceService()
