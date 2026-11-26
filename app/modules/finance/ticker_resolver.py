"""
app/modules/finance/ticker_resolver.py
Enterprise Ticker & Entity Resolution Engine
Maps natural-language company names, indices, and aliases to canonical exchange tickers.
"""

import re
from typing import Optional, Tuple
from app.modules.finance.schemas import AssetType

# =========================================================================
# CANONICAL TICKER REGISTRY (Indian Equities, Indices, US Blue-chips, Crypto)
# Key: Normalized lowercase alias -> Value: (canonical_symbol, display_name, exchange, currency, asset_type)
# =========================================================================

EQUITY_REGISTRY: dict[str, Tuple[str, str, str, str, AssetType]] = {
    # ------------------ Major Indian Indices ------------------
    "nifty": ("^NSEI", "NIFTY 50", "NSE", "INR", AssetType.INDEX),
    "nifty 50": ("^NSEI", "NIFTY 50", "NSE", "INR", AssetType.INDEX),
    "nifty50": ("^NSEI", "NIFTY 50", "NSE", "INR", AssetType.INDEX),
    "sensex": ("^BSESN", "BSE SENSEX", "BSE", "INR", AssetType.INDEX),
    "bse sensex": ("^BSESN", "BSE SENSEX", "BSE", "INR", AssetType.INDEX),
    "bank nifty": ("^NSEBANK", "NIFTY BANK", "NSE", "INR", AssetType.INDEX),
    "banknifty": ("^NSEBANK", "NIFTY BANK", "NSE", "INR", AssetType.INDEX),
    "nifty it": ("^CNXIT", "NIFTY IT", "NSE", "INR", AssetType.INDEX),
    "nifty auto": ("^CNXAUTO", "NIFTY AUTO", "NSE", "INR", AssetType.INDEX),
    "nifty metal": ("^CNXMETAL", "NIFTY METAL", "NSE", "INR", AssetType.INDEX),
    "nifty pharma": ("^CNXPHARMA", "NIFTY PHARMA", "NSE", "INR", AssetType.INDEX),
    "nifty midcap": ("NIFTY_MIDCAP_100.NS", "NIFTY MIDCAP 100", "NSE", "INR", AssetType.INDEX),

    # ------------------ Top Indian Equities (NSE) ------------------
    "reliance": ("RELIANCE.NS", "Reliance Industries Limited", "NSE", "INR", AssetType.EQUITY),
    "reliance industries": ("RELIANCE.NS", "Reliance Industries Limited", "NSE", "INR", AssetType.EQUITY),
    "ril": ("RELIANCE.NS", "Reliance Industries Limited", "NSE", "INR", AssetType.EQUITY),

    "tcs": ("TCS.NS", "Tata Consultancy Services Limited", "NSE", "INR", AssetType.EQUITY),
    "tata consultancy": ("TCS.NS", "Tata Consultancy Services Limited", "NSE", "INR", AssetType.EQUITY),

    "hdfc": ("HDFCBANK.NS", "HDFC Bank Limited", "NSE", "INR", AssetType.EQUITY),
    "hdfc bank": ("HDFCBANK.NS", "HDFC Bank Limited", "NSE", "INR", AssetType.EQUITY),

    "icici": ("ICICIBANK.NS", "ICICI Bank Limited", "NSE", "INR", AssetType.EQUITY),
    "icici bank": ("ICICIBANK.NS", "ICICI Bank Limited", "NSE", "INR", AssetType.EQUITY),

    "infosys": ("INFY.NS", "Infosys Limited", "NSE", "INR", AssetType.EQUITY),
    "infy": ("INFY.NS", "Infosys Limited", "NSE", "INR", AssetType.EQUITY),

    "sbi": ("SBIN.NS", "State Bank of India", "NSE", "INR", AssetType.EQUITY),
    "state bank of india": ("SBIN.NS", "State Bank of India", "NSE", "INR", AssetType.EQUITY),
    "state bank": ("SBIN.NS", "State Bank of India", "NSE", "INR", AssetType.EQUITY),

    "itc": ("ITC.NS", "ITC Limited", "NSE", "INR", AssetType.EQUITY),

    "bharti airtel": ("BHARTIARTL.NS", "Bharti Airtel Limited", "NSE", "INR", AssetType.EQUITY),
    "airtel": ("BHARTIARTL.NS", "Bharti Airtel Limited", "NSE", "INR", AssetType.EQUITY),

    "l&t": ("LT.NS", "Larsen & Toubro Limited", "NSE", "INR", AssetType.EQUITY),
    "larsen": ("LT.NS", "Larsen & Toubro Limited", "NSE", "INR", AssetType.EQUITY),
    "larsen and toubro": ("LT.NS", "Larsen & Toubro Limited", "NSE", "INR", AssetType.EQUITY),

    "tata motors": ("TMCV.NS", "Tata Motors Limited", "NSE", "INR", AssetType.EQUITY),
    "tatamotors": ("TMCV.NS", "Tata Motors Limited", "NSE", "INR", AssetType.EQUITY),
    "tata motors cv": ("TMCV.NS", "Tata Motors Limited (Commercial Vehicles)", "NSE", "INR", AssetType.EQUITY),
    "tata motors pv": ("TMPV.NS", "Tata Motors Passenger Vehicles Limited", "NSE", "INR", AssetType.EQUITY),

    "tata steel": ("TATASTEEL.NS", "Tata Steel Limited", "NSE", "INR", AssetType.EQUITY),
    "tata power": ("TATAPOWER.NS", "Tata Power Company Limited", "NSE", "INR", AssetType.EQUITY),
    "tata tech": ("TATATECH.NS", "Tata Technologies Limited", "NSE", "INR", AssetType.EQUITY),
    "tata technologies": ("TATATECH.NS", "Tata Technologies Limited", "NSE", "INR", AssetType.EQUITY),

    "maruti": ("MARUTI.NS", "Maruti Suzuki India Limited", "NSE", "INR", AssetType.EQUITY),
    "maruti suzuki": ("MARUTI.NS", "Maruti Suzuki India Limited", "NSE", "INR", AssetType.EQUITY),

    "mahindra": ("M&M.NS", "Mahindra & Mahindra Limited", "NSE", "INR", AssetType.EQUITY),
    "m&m": ("M&M.NS", "Mahindra & Mahindra Limited", "NSE", "INR", AssetType.EQUITY),

    "bajaj finance": ("BAJFINANCE.NS", "Bajaj Finance Limited", "NSE", "INR", AssetType.EQUITY),
    "bajaj finserv": ("BAJAJFINSV.NS", "Bajaj Finserv Limited", "NSE", "INR", AssetType.EQUITY),
    "bajaj auto": ("BAJAJ-AUTO.NS", "Bajaj Auto Limited", "NSE", "INR", AssetType.EQUITY),

    "adani enterprises": ("ADANIENT.NS", "Adani Enterprises Limited", "NSE", "INR", AssetType.EQUITY),
    "adani ports": ("ADANIPORTS.NS", "Adani Ports and Special Economic Zone", "NSE", "INR", AssetType.EQUITY),
    "adani green": ("ADANIGREEN.NS", "Adani Green Energy Limited", "NSE", "INR", AssetType.EQUITY),
    "adani power": ("ADANIPOWER.NS", "Adani Power Limited", "NSE", "INR", AssetType.EQUITY),
    "adani": ("ADANIENT.NS", "Adani Enterprises Limited", "NSE", "INR", AssetType.EQUITY),

    "zomato": ("ZOMATO.NS", "Zomato Limited", "NSE", "INR", AssetType.EQUITY),
    "swiggy": ("SWIGGY.NS", "Swiggy Limited", "NSE", "INR", AssetType.EQUITY),
    "paytm": ("PAYTM.NS", "One 97 Communications Limited (Paytm)", "NSE", "INR", AssetType.EQUITY),
    "nykaa": ("NYKAA.NS", "FSN E-Commerce Ventures Limited (Nykaa)", "NSE", "INR", AssetType.EQUITY),
    "ola electric": ("OLAELEC.NS", "Ola Electric Mobility Limited", "NSE", "INR", AssetType.EQUITY),

    "irfc": ("IRFC.NS", "Indian Railway Finance Corporation", "NSE", "INR", AssetType.EQUITY),
    "rvnl": ("RVNL.NS", "Rail Vikas Nigam Limited", "NSE", "INR", AssetType.EQUITY),
    "suzlon": ("SUZLON.NS", "Suzlon Energy Limited", "NSE", "INR", AssetType.EQUITY),
    "ireda": ("IREDA.NS", "Indian Renewable Energy Dev Agency", "NSE", "INR", AssetType.EQUITY),
    "bhel": ("BHEL.NS", "Bharat Heavy Electricals Limited", "NSE", "INR", AssetType.EQUITY),
    "hal": ("HAL.NS", "Hindustan Aeronautics Limited", "NSE", "INR", AssetType.EQUITY),
    "bel": ("BEL.NS", "Bharat Electronics Limited", "NSE", "INR", AssetType.EQUITY),

    "wipro": ("WIPRO.NS", "Wipro Limited", "NSE", "INR", AssetType.EQUITY),
    "hcl tech": ("HCLTECH.NS", "HCL Technologies Limited", "NSE", "INR", AssetType.EQUITY),
    "tech mahindra": ("TECHM.NS", "Tech Mahindra Limited", "NSE", "INR", AssetType.EQUITY),

    "asian paints": ("ASIANPAINT.NS", "Asian Paints Limited", "NSE", "INR", AssetType.EQUITY),
    "titan": ("TITAN.NS", "Titan Company Limited", "NSE", "INR", AssetType.EQUITY),
    "ultratech": ("ULTRACEMCO.NS", "UltraTech Cement Limited", "NSE", "INR", AssetType.EQUITY),
    "sun pharma": ("SUNPHARMA.NS", "Sun Pharmaceutical Industries", "NSE", "INR", AssetType.EQUITY),
    "cipla": ("CIPLA.NS", "Cipla Limited", "NSE", "INR", AssetType.EQUITY),

    "mrf": ("MRF.NS", "MRF Limited", "NSE", "INR", AssetType.EQUITY),
    "vedanta": ("VEDL.NS", "Vedanta Limited", "NSE", "INR", AssetType.EQUITY),
    "jsw steel": ("JSWSTEEL.NS", "JSW Steel Limited", "NSE", "INR", AssetType.EQUITY),
    "hindalco": ("HINDALCO.NS", "Hindalco Industries Limited", "NSE", "INR", AssetType.EQUITY),
    "ntpc": ("NTPC.NS", "NTPC Limited", "NSE", "INR", AssetType.EQUITY),
    "power grid": ("POWERGRID.NS", "Power Grid Corporation of India", "NSE", "INR", AssetType.EQUITY),
    "coal india": ("COALINDIA.NS", "Coal India Limited", "NSE", "INR", AssetType.EQUITY),
    "ongc": ("ONGC.NS", "Oil & Natural Gas Corporation", "NSE", "INR", AssetType.EQUITY),

    # ------------------ Global Tech & US Equities ------------------
    "apple": ("AAPL", "Apple Inc.", "NASDAQ", "USD", AssetType.EQUITY),
    "aapl": ("AAPL", "Apple Inc.", "NASDAQ", "USD", AssetType.EQUITY),
    "microsoft": ("MSFT", "Microsoft Corporation", "NASDAQ", "USD", AssetType.EQUITY),
    "msft": ("MSFT", "Microsoft Corporation", "NASDAQ", "USD", AssetType.EQUITY),
    "google": ("GOOGL", "Alphabet Inc.", "NASDAQ", "USD", AssetType.EQUITY),
    "alphabet": ("GOOGL", "Alphabet Inc.", "NASDAQ", "USD", AssetType.EQUITY),
    "amazon": ("AMZN", "Amazon.com Inc.", "NASDAQ", "USD", AssetType.EQUITY),
    "amzn": ("AMZN", "Amazon.com Inc.", "NASDAQ", "USD", AssetType.EQUITY),
    "nvidia": ("NVDA", "NVIDIA Corporation", "NASDAQ", "USD", AssetType.EQUITY),
    "nvda": ("NVDA", "NVIDIA Corporation", "NASDAQ", "USD", AssetType.EQUITY),
    "tesla": ("TSLA", "Tesla Inc.", "NASDAQ", "USD", AssetType.EQUITY),
    "tsla": ("TSLA", "Tesla Inc.", "NASDAQ", "USD", AssetType.EQUITY),
    "meta": ("META", "Meta Platforms Inc.", "NASDAQ", "USD", AssetType.EQUITY),
    "netflix": ("NFLX", "Netflix Inc.", "NASDAQ", "USD", AssetType.EQUITY),

    # ------------------ Global Indices ------------------
    "sp500": ("^GSPC", "S&P 500", "INDEX", "USD", AssetType.INDEX),
    "s&p 500": ("^GSPC", "S&P 500", "INDEX", "USD", AssetType.INDEX),
    "nasdaq": ("^IXIC", "NASDAQ Composite", "INDEX", "USD", AssetType.INDEX),
    "dow jones": ("^DJI", "Dow Jones Industrial Average", "INDEX", "USD", AssetType.INDEX),

    # ------------------ Crypto & Commodities ------------------
    "bitcoin": ("BTC-USD", "Bitcoin", "CRYPTO", "USD", AssetType.CRYPTO),
    "btc": ("BTC-USD", "Bitcoin", "CRYPTO", "USD", AssetType.CRYPTO),
    "ethereum": ("ETH-USD", "Ethereum", "CRYPTO", "USD", AssetType.CRYPTO),
    "eth": ("ETH-USD", "Ethereum", "CRYPTO", "USD", AssetType.CRYPTO),
    "solana": ("SOL-USD", "Solana", "CRYPTO", "USD", AssetType.CRYPTO),
    "sol": ("SOL-USD", "Solana", "CRYPTO", "USD", AssetType.CRYPTO),
    "gold": ("GC=F", "Gold Futures", "COMEX", "USD", AssetType.COMMODITY),
    "silver": ("SI=F", "Silver Futures", "COMEX", "USD", AssetType.COMMODITY),
    "crude oil": ("CL=F", "Crude Oil Futures", "NYMEX", "USD", AssetType.COMMODITY),
}


class TickerResolver:
    """
    Silicon Valley standard entity parser & fuzzy ticker resolver.
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """Removes punctuation and extra whitespace for clean dictionary lookup."""
        clean = re.sub(r"[^\w\s\^\-\.]", " ", text.lower())
        return " ".join(clean.split())

    @classmethod
    def resolve_from_query(
        cls,
        query: str,
        allow_live_search: bool = False
    ) -> Optional[Tuple[str, str, str, str, AssetType]]:
        """
        Extracts company/asset entity from user natural language query and resolves to canonical ticker.
        Returns: (symbol, name, exchange, currency, asset_type) or None if no match.
        """
        norm_q = cls.normalize_text(query)

        # 1. Exact match in full query (e.g. "reliance")
        if norm_q in EQUITY_REGISTRY:
            return EQUITY_REGISTRY[norm_q]

        # 2. Check for longer phrases first (e.g. "tata motors" before "tata")
        sorted_keys = sorted(EQUITY_REGISTRY.keys(), key=lambda k: len(k), reverse=True)
        for key in sorted_keys:
            pattern = rf"\b{re.escape(key)}\b"
            if re.search(pattern, norm_q):
                return EQUITY_REGISTRY[key]

        # 3. Direct ticker symbol pattern matching (e.g. RELIANCE.NS, ^NSEI, AAPL, BTC-USD)
        direct_ticker_match = re.search(r"\b([A-Z0-9\^]{2,10}(\.NS|\.BO|-USD)?)\b", query)
        if direct_ticker_match:
            cand = direct_ticker_match.group(1).upper()
            if cand.endswith((".NS", ".BO")):
                return (cand, cand, "NSE" if cand.endswith(".NS") else "BSE", "INR", AssetType.EQUITY)
            if cand.startswith("^"):
                return (cand, cand, "INDEX", "INR", AssetType.INDEX)

        # 4. Dynamic Live Search Fallback (Only executed when explicitly allowed during quote fetch)
        if allow_live_search:
            try:
                # Strip common stop words to isolate company candidate
                cleaned = re.sub(
                    r"\b(share|stock|equity|price|rate|quote|today|target|analysis|value|ka|ki|ke|kya|hai|kitna|aaj|current|live)\b",
                    "",
                    norm_q,
                    flags=re.IGNORECASE
                ).strip()
                if cleaned and len(cleaned) >= 2:
                    import yfinance as yf
                    search_res = yf.Search(cleaned)
                    if search_res and getattr(search_res, "quotes", None):
                        top = search_res.quotes[0]
                        sym = top.get("symbol")
                        short_name = top.get("shortname") or top.get("longname") or sym
                        exch = top.get("exchDisp") or ("NSE" if str(sym).endswith(".NS") else "US")
                        curr = "INR" if str(sym).endswith((".NS", ".BO")) else "USD"
                        return (sym, short_name, exch, curr, AssetType.EQUITY)
            except Exception:
                pass

        return None


ticker_resolver = TickerResolver()
