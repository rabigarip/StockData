"""Scrape last price for the 6 Yahoo-blind GCC indices from Investing.com.

Runs on GitHub Actions (residential IP). Writes index_snapshots.json
{bloomberg: {"last": float, "asof": "YYYY-MM-DD", "name": str}} for the indices
whose scraped value passes a sanity check against the reference level (catches a
wrong slug pointing at the wrong index). indices_refresh.py reads this file.
"""
from __future__ import annotations
import json, time, re
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as creq
from bs4 import BeautifulSoup

import indices_config as IC

HERE = Path(__file__).resolve().parent
OUT = HERE / "index_snapshots.json"
DELAY = 3.0


def _fetch_last(slug: str):
    """Return (last_price, page_name) from the Investing.com index page."""
    url = f"https://www.investing.com/indices/{slug}"
    try:
        r = creq.get(url, impersonate="chrome", timeout=25)
    except Exception as e:
        return None, f"ERR {type(e).__name__}"
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    soup = BeautifulSoup(r.text, "lxml")
    el = soup.select_one('[data-test="instrument-price-last"]')
    h1 = soup.find("h1")
    name = h1.get_text(strip=True) if h1 else ""
    if not el:
        return None, name or "no-price-element"
    try:
        return float(el.get_text(strip=True).replace(",", "")), name
    except ValueError:
        return None, name


def main() -> int:
    out = {}
    asof = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    blind = {b: v for b, v in IC.INDICES.items() if v[2] is None}  # yahoo symbol None
    print(f"Scraping {len(blind)} blind indices from Investing.com\n", flush=True)
    for bbg, (name, market, _y, slug) in blind.items():
        last, page = _fetch_last(slug)
        ref = IC.REFERENCE.get(bbg)
        # Sanity gate: scraped value within ±35% of the reference level (allows
        # market drift, rejects a slug that resolved to a totally different index).
        ok = last is not None and ref and 0.65 * ref <= last <= 1.35 * ref
        if ok:
            out[bbg] = {"last": round(last, 2), "asof": asof, "name": page}
            print(f"  {bbg:9} {last:>10.2f}  OK  ({page[:30]})", flush=True)
        else:
            print(f"  {bbg:9} {str(last):>10}  REJECT slug='{slug}' ref={ref} page='{page[:30]}'", flush=True)
        time.sleep(DELAY)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {OUT} — {len(out)}/{len(blind)} indices validated", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
