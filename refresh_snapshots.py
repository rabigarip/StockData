"""Refresh MarketScreener snapshots for the 60 GCC names — with validation.

Runs on GitHub Actions (residential IP). For each name it resolves a MarketScreener
slug via curated id -> ISIN search -> name/ticker search, and VALIDATES every
candidate against the expected company (name/ISIN/country) before scraping. This
is the engine's own pipeline order; an earlier version trusted the raw ISIN hit
and committed 29 wrong-company snapshots ("Liftoff Mobile" etc.) — validation
prevents that: a name that can't be validated is skipped, never mis-scraped.

Snapshots write to the engine root's data/marketscreener/ (MS_TRACKED_REFRESH=1)
as the lean ms_<ticker>_<page>.html; the workflow copies them into this repo.
"""
from __future__ import annotations
import os, time

os.environ.setdefault("MS_TRACKED_REFRESH", "1")
os.environ.setdefault("MS_USE_CURL_CFFI", "1")

import gcc_paths  # noqa: E402  (sets sys.path to engine root)
from engine_data import _master, engine_ticker  # noqa: E402
from ticker_map import MAP  # noqa: E402
from src.providers.marketscreener_pages import (  # noqa: E402
    fetch_financial_forecast_series, fetch_calendar_events, fetch_summary_page,
    resolve_marketscreener_by_isin, resolve_slug_from_search,
)
from src.services.entity_resolution import validate_candidate_page  # noqa: E402

PAGE_DELAY = float(os.environ.get("MS_PAGE_DELAY", "3"))


def _long_prefix(ticker: str, isin: str, slug: str) -> str:
    t = ticker.replace(".", "_")
    i = (isin or "noisin").strip() or "noisin"
    return f"ms_{t}_{i}_{slug}"


def _candidates(et: str, rec: dict):
    """Yield (how, slug) candidates in priority order."""
    cid = (rec.get("marketscreener_id") or "").strip()
    if cid:
        yield "curated", cid
    isin = (rec.get("isin") or "").strip()
    if isin:
        try:
            r = resolve_marketscreener_by_isin(isin)
            if r:
                yield "isin", r[0]
        except Exception:
            pass
        time.sleep(1)
    try:
        s = resolve_slug_from_search(et, company_name=rec.get("company_name", ""))
        if s:
            yield "search", s
    except Exception:
        pass


def _validated_slug(et: str, rec: dict):
    """Return (slug, how) for the first candidate that validates, else (None, None)."""
    for how, slug in _candidates(et, rec):
        url = f"https://www.marketscreener.com/quote/stock/{slug}/"
        try:
            vr = validate_candidate_page(rec, slug, url,
                                         cache_name=f"validate_{et.replace('.', '_')}")
            if getattr(vr, "valid", False):
                return slug, how
        except Exception:
            continue
        time.sleep(1)
    return None, None


def main() -> int:
    master = _master()
    tickers = list(dict.fromkeys(engine_ticker(yh) for yh, _b in MAP.values()))
    print(f"Refreshing MS snapshots for {len(tickers)} GCC names (with validation)\n", flush=True)

    scraped, unresolved = 0, []
    for i, et in enumerate(tickers, 1):
        rec = master.get(et)
        if not rec:
            print(f"[{i}/{len(tickers)}] {et}: NO company_master record", flush=True)
            unresolved.append(et); continue

        slug, how = _validated_slug(et, rec)
        if not slug:
            print(f"[{i}/{len(tickers)}] {et}: UNRESOLVED (no candidate validated)", flush=True)
            unresolved.append(et); continue

        base = f"https://www.marketscreener.com/quote/stock/{slug}"
        prefix = _long_prefix(et, rec.get("isin", ""), slug)
        oks = []
        for name, fn in (("finances", fetch_financial_forecast_series),
                         ("calendar", fetch_calendar_events),
                         ("summary",  fetch_summary_page)):
            try:
                _, st = fn(base, cache_key_prefix=prefix)
                oks.append(f"{name}:{st.status}")
                if st.status in ("success", "partial"):
                    scraped += 1
            except Exception as e:
                oks.append(f"{name}:ERR({type(e).__name__})")
            time.sleep(PAGE_DELAY)
        print(f"[{i}/{len(tickers)}] {et} -> {slug} [{how}]  {'  '.join(oks)}", flush=True)

    print(f"\nDone. pages scraped ok: {scraped}. unresolved: {len(unresolved)} {unresolved}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
