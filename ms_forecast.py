"""Forward + historical revenue/net-income from MarketScreener finances snapshots.

The engine's GitHub Actions workflow scrapes MS /finances/ (residential IP) and
commits HTML snapshots to data/marketscreener/. We read those snapshots locally
(no live fetch, no Cloudflare block) and extract the annual + quarterly series —
which carries the forward estimates the sheet's …E columns need, plus historical
actuals for bank-gap / blind-name backfill.

Snapshot cache key = ticker-form prefix, e.g. '2222_SR', 'ADNOCLS_AE'.
"""
from __future__ import annotations
import gcc_paths
gcc_paths.use_gcc_snapshots()  # read snapshots from this repo's data/marketscreener
from src.providers.marketscreener_pages import fetch_financial_forecast_series
from engine_data import lookup, engine_ticker


def _prefix(yahoo_symbol: str) -> str:
    return engine_ticker(yahoo_symbol).replace(".", "_")


def forecast_for(yahoo_symbol: str) -> dict:
    """Return {'annual': {label: {'revenue','net_income'}}, 'quarterly': {...}}.

    Labels normalised to the sheet's grammar: annual 'FY2026', quarterly '2026-Q2'.
    Empty dict if no snapshot exists for this name.
    """
    rec = lookup(yahoo_symbol)
    slug = (rec or {}).get("marketscreener_id") or "x"
    base = f"https://www.marketscreener.com/quote/stock/{slug}"
    try:
        payload, status = fetch_financial_forecast_series(base, cache_key_prefix=_prefix(yahoo_symbol))
    except Exception:
        return {}
    if not payload or status.status not in ("success", "partial"):
        return {}

    # Scale MS values (usually 'million') to absolute, matching Yahoo's units so
    # estimate and actual columns are internally consistent.
    scale = {"thousand": 1e3, "million": 1e6, "billion": 1e9}.get(
        str(payload.get("unit_scale", "")).lower(), 1.0)

    def _series(block: dict, normalise) -> dict:
        out = {}
        periods = (block or {}).get("periods") or []
        rev = (block or {}).get("net_sales") or []
        ni = (block or {}).get("net_income") or []
        for i, p in enumerate(periods):
            lbl = normalise(p)
            if not lbl:
                continue
            out[lbl] = {
                "revenue": rev[i] * scale if i < len(rev) and rev[i] is not None else None,
                "net_income": ni[i] * scale if i < len(ni) and ni[i] is not None else None,
            }
        return out

    def _norm_annual(p):       # "FY2026" -> "FY2026"
        return p if str(p).startswith("FY") else f"FY{p}"

    def _norm_quarter(p):      # "2026Q2" -> "2026-Q2"
        s = str(p)
        if "Q" in s and "-" not in s:
            yr, q = s.split("Q")
            return f"{yr}-Q{q}"
        return s

    return {
        "annual":    _series(payload.get("annual"), _norm_annual),
        "quarterly": _series(payload.get("quarterly"), _norm_quarter),
    }
