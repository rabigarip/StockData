"""Last-close price from the MarketScreener summary snapshot.

Used for the blind UAE/Oman names that Yahoo doesn't price. Reads the committed
ms_<ticker>_summary.html snapshot — no live fetch.
"""
from __future__ import annotations
import gcc_paths
gcc_paths.use_gcc_snapshots()
from src.providers.marketscreener_pages import fetch_summary_page
from engine_data import engine_ticker


def price_for(yahoo_symbol: str):
    """Return last close price (float) from the MS summary snapshot, or None."""
    tf = engine_ticker(yahoo_symbol).replace(".", "_")
    try:
        payload, status = fetch_summary_page(
            "https://www.marketscreener.com/quote/stock/x", cache_key_prefix=tf)
    except Exception:
        return None
    if status.status not in ("success", "partial"):
        return None
    return payload.get("last_close_price")
