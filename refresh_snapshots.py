"""Refresh MarketScreener snapshots for the 60 GCC names.

Runs on GitHub Actions (residential IP — MarketScreener Cloudflare-blocks Macs
and datacenter IPs). Self-contained: resolves each MS slug from company_master's
marketscreener_id, else from ISIN — no earnings.db, no engine CLI scripts (those
assume a DB + PYTHONPATH that a bare submodule checkout doesn't have, which is
why the first Action produced nothing).

Snapshots are written by the engine (MS_TRACKED_REFRESH=1) to the engine root's
data/marketscreener/ as the lean ms_<ticker>_<page>.html name; the workflow then
copies them into this repo and commits.
"""
from __future__ import annotations
import os, sys, time

os.environ.setdefault("MS_TRACKED_REFRESH", "1")  # commit each successful HTML
os.environ.setdefault("MS_USE_CURL_CFFI", "1")    # Chrome TLS -> pass Cloudflare

import gcc_paths  # noqa: E402  (sets sys.path to the engine root)
from engine_data import _master, engine_ticker  # noqa: E402
from ticker_map import MAP  # noqa: E402
from src.providers.marketscreener_pages import (  # noqa: E402
    fetch_financial_forecast_series,
    fetch_calendar_events,
    fetch_summary_page,
    resolve_marketscreener_by_isin,
)

PAGE_DELAY = float(os.environ.get("MS_PAGE_DELAY", "3"))


def _long_prefix(ticker: str, isin: str, slug: str) -> str:
    # Matches the engine's _cache_key_prefix so _write_snapshot emits the lean
    # ms_<ticker>_<page>.html the runtime loader reads.
    t = ticker.replace(".", "_")
    i = (isin or "noisin").strip() or "noisin"
    return f"ms_{t}_{i}_{slug}"


def main() -> int:
    master = _master()
    tickers = list(dict.fromkeys(engine_ticker(yh) for yh, _blind in MAP.values()))
    print(f"Refreshing MS snapshots for {len(tickers)} GCC names\n", flush=True)

    unresolved, scraped = [], 0
    for i, et in enumerate(tickers, 1):
        rec = master.get(et)
        if not rec:
            print(f"[{i}/{len(tickers)}] {et}: NO company_master record", flush=True)
            unresolved.append(et); continue

        slug = (rec.get("marketscreener_id") or "").strip()
        isin = (rec.get("isin") or "").strip()
        if not slug and isin:
            try:
                r = resolve_marketscreener_by_isin(isin)
                slug = r[0] if r else ""
            except Exception as e:
                print(f"[{i}/{len(tickers)}] {et}: ISIN resolve error {type(e).__name__}", flush=True)
            time.sleep(2)
        if not slug:
            print(f"[{i}/{len(tickers)}] {et}: SLUG UNRESOLVED (isin={isin or 'none'})", flush=True)
            unresolved.append(et); continue

        base = f"https://www.marketscreener.com/quote/stock/{slug}"
        prefix = _long_prefix(et, isin, slug)
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
        print(f"[{i}/{len(tickers)}] {et} -> {slug}  {'  '.join(oks)}", flush=True)

    print(f"\nDone. pages scraped ok: {scraped}. unresolved names: {len(unresolved)} {unresolved}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
