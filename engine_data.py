"""Join the GCC ticker map to the engine's company_master.json.

Provides, per name: engine ticker, ISIN, marketscreener_id, currency, is_bank.
Handles the suffix gap — Yahoo uses .AD/.DU for UAE, the engine uses .AE.
"""
from __future__ import annotations
import json
from functools import lru_cache
import gcc_paths

CM_PATH = str(gcc_paths.ENGINE_ROOT / "data" / "company_master.json")


def engine_ticker(yahoo_symbol: str) -> str:
    """Map a Yahoo symbol to the engine's ticker convention (UAE -> .AE)."""
    for suf in (".AD", ".DU"):
        if yahoo_symbol.endswith(suf):
            return yahoo_symbol[: -len(suf)] + ".AE"
    return yahoo_symbol


@lru_cache(maxsize=1)
def _master() -> dict[str, dict]:
    data = json.load(open(CM_PATH))
    recs = data if isinstance(data, list) else list(data.values())
    return {r.get("ticker"): r for r in recs}


def lookup(yahoo_symbol: str) -> dict | None:
    """Return the company_master record for a name, or None if not onboarded."""
    m = _master()
    return m.get(yahoo_symbol) or m.get(engine_ticker(yahoo_symbol))
