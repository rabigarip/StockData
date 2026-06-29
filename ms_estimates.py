"""MarketScreener forward estimates for a name, via the engine's scraper.

Returns {"FY2026": FinancialPeriod, ...} for is_consensus periods, reading
from the engine's MS cache. Names without a resolved marketscreener_id return
{} (flagged 'pending onboarding' — see refresh_marketscreener_cache.py batch).
"""
from __future__ import annotations
from src.providers.marketscreener import fetch_consensus
from engine_data import lookup


def estimates_for(yahoo_symbol: str) -> dict:
    """{'FY2026': fp, 'FY2027': fp, ...} of consensus periods, or {} if unavailable."""
    rec = lookup(yahoo_symbol)
    if not rec:
        return {}
    ms_id = rec.get("marketscreener_id")
    if not ms_id:
        return {}
    try:
        periods, _diag = fetch_consensus(
            ms_id,
            currency=rec.get("currency", "USD"),
            is_bank=bool(rec.get("is_bank")),
            ticker=rec.get("ticker"),
            company_name=rec.get("company_name"),
            isin=rec.get("isin"),
        )
    except Exception:
        return {}
    out = {}
    for p in (periods or []):
        if p.is_consensus:                      # forward estimate only
            out[p.period_label] = p
    return out
