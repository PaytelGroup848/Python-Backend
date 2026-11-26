"""
app/modules/finance/schemas.py
Enterprise Silicon Valley Market Data Schema
Defines strict, immutable models for financial equities, indices, and quotes.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MarketStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PRE_MARKET = "PRE_MARKET"
    AFTER_HOURS = "AFTER_HOURS"


class AssetType(str, Enum):
    EQUITY = "EQUITY"
    INDEX = "INDEX"
    ETF = "ETF"
    CRYPTO = "CRYPTO"
    COMMODITY = "COMMODITY"
    CURRENCY = "CURRENCY"


class StockQuote(BaseModel):
    """
    Standardized, normalized market quote model across NSE, BSE, US & Global exchanges.
    """
    symbol: str = Field(..., description="Canonical exchange ticker (e.g. RELIANCE.NS, ^NSEI, AAPL)")
    name: str = Field(..., description="Full legal company or asset name")
    exchange: str = Field(..., description="Primary trading exchange (e.g. NSE, BSE, NASDAQ, NYSE, INDEX)")
    currency: str = Field(default="INR", description="Trading currency (e.g. INR, USD)")
    asset_type: AssetType = Field(default=AssetType.EQUITY)

    # Core Pricing Metrics
    current_price: float = Field(..., description="Last traded price (LTP)")
    previous_close: Optional[float] = None
    open_price: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None

    # Performance
    change: float = Field(default=0.0, description="Absolute price change from previous close")
    percent_change: float = Field(default=0.0, description="Percentage change from previous close")
    is_positive: bool = Field(default=True, description="True if price is up or unchanged")

    # Volume & Valuation
    volume: Optional[int] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    pe_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    market_cap_formatted: Optional[str] = None

    # Temporal & Status Metadata
    market_status: MarketStatus = Field(default=MarketStatus.CLOSED)
    timestamp_ist: str = Field(..., description="Human-readable timestamp in Indian Standard Time (IST)")
    is_stale: bool = Field(default=False, description="True if data is fallback cached / offline")
