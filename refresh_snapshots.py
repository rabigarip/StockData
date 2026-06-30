"""Refresh MarketScreener snapshots for the 60 GCC names — scrape-then-verify.

Runs on GitHub Actions (residential IP). For each name it tries candidate slugs
(curated id -> ISIN search -> name search); for each candidate it scrapes the
finances page and checks the page's own <title> against the expected company
(name tokens OR the numeric Tadawul code). The first candidate that matches is
kept and its other pages scraped; if none match, the scraped file is deleted so
nothing wrong is committed.

Why title-check and not validate_candidate_page: that validator does a separate
fetch that the runner's IP gets blocked on, so it rejected EVERYTHING (0/60).
The title check reuses the page we already fetched via the working curl_cffi
path — the same check that caught the 29 corrupt snapshots.
"""
from __future__ import annotations
import os, re, time, gzip
from pathlib import Path

os.environ.setdefault("MS_TRACKED_REFRESH", "1")
os.environ.setdefault("MS_USE_CURL_CFFI", "1")

import gcc_paths  # noqa: E402
from engine_data import _master, engine_ticker  # noqa: E402
from ticker_map import MAP  # noqa: E402
from src.providers.marketscreener_pages import (  # noqa: E402
    fetch_financial_forecast_series, fetch_calendar_events, fetch_summary_page,
    resolve_marketscreener_by_isin, resolve_slug_from_search,
)

PAGE_DELAY = float(os.environ.get("MS_PAGE_DELAY", "3"))
ENGINE_SNAP = gcc_paths.ENGINE_ROOT / "data" / "marketscreener"

# Names not in company_master — expected names for the title check / name search.
FALLBACK_NAMES = {
    "NBK.KW": "National Bank of Kuwait", "ZAIN.KW": "Mobile Telecommunications Zain",
    "MABANEE.KW": "Mabanee", "EMIRATESNBD.AE": "Emirates NBD",
    "ADIB.AE": "Abu Dhabi Islamic Bank", "EMAARDEV.AE": "Emaar Development",
    "SALIK.AE": "Salik",
}
STOP = {"the","company","co","for","and","plc","pjsc","saog","group","sa","ltd",
        "public","joint","stock","cooperative","insurance","limited","bank","com",
        "holding","corporation","corp","services","industries","industry","p","q","s","c"}


def _toks(s):
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if w not in STOP and len(w) > 2}


def _finances_title(tf: str) -> str | None:
    p = ENGINE_SNAP / f"ms_{tf}_finances.html"
    raw = None
    if p.exists():
        raw = p.read_text("utf-8", errors="ignore")
    elif p.with_suffix(".html.gz").exists():
        raw = gzip.decompress(p.with_suffix(".html.gz").read_bytes()).decode("utf-8", "ignore")
    if not raw:
        return None
    m = re.search(r"<title>(.*?)</title>", raw, re.I | re.S)
    return m.group(1).strip() if m else ""


def _matches(expected: str, code: str, title: str | None) -> bool:
    if not title:
        return False
    if _toks(expected) & _toks(title):
        return True
    return bool(code and code.isdigit() and re.search(rf"\b{code}\b", title))


def _candidate_slugs(et: str, rec: dict, name: str):
    cid = (rec.get("marketscreener_id") or "").strip()
    if cid:
        yield cid
    isin = (rec.get("isin") or "").strip()
    if isin:
        try:
            r = resolve_marketscreener_by_isin(isin)
            if r:
                yield r[0]
        except Exception:
            pass
        time.sleep(1)
    try:
        s = resolve_slug_from_search(et, company_name=name)
        if s:
            yield s
    except Exception:
        pass


def _purge(tf: str):
    for f in ENGINE_SNAP.glob(f"ms_{tf}_*"):
        try: f.unlink()
        except Exception: pass


def main() -> int:
    master = _master()
    tickers = list(dict.fromkeys(engine_ticker(yh) for yh, _b in MAP.values()))
    print(f"Refreshing MS snapshots for {len(tickers)} GCC names (scrape-then-verify)\n", flush=True)

    resolved, unresolved = 0, []
    for i, et in enumerate(tickers, 1):
        rec = master.get(et) or {}
        name = rec.get("company_name") or FALLBACK_NAMES.get(et, "")
        code = et.split(".")[0]
        tf = et.replace(".", "_")
        if not name and not rec:
            print(f"[{i}/{len(tickers)}] {et}: NO name/record — skip", flush=True)
            unresolved.append(et); continue

        hit = None
        for slug in _candidate_slugs(et, rec, name):
            base = f"https://www.marketscreener.com/quote/stock/{slug}"
            prefix = f"ms_{tf}_{(rec.get('isin') or 'noisin').strip() or 'noisin'}_{slug}"
            try:
                fetch_financial_forecast_series(base, cache_key_prefix=prefix)
            except Exception:
                pass
            time.sleep(PAGE_DELAY)
            if _matches(name, code, _finances_title(tf)):
                hit = (slug, base, prefix); break

        if not hit:
            _purge(tf)  # drop any wrong write so nothing bad is committed
            print(f"[{i}/{len(tickers)}] {et}: UNRESOLVED", flush=True)
            unresolved.append(et); continue

        slug, base, prefix = hit
        for fn in (fetch_calendar_events, fetch_summary_page):
            try: fn(base, cache_key_prefix=prefix)
            except Exception: pass
            time.sleep(PAGE_DELAY)
        resolved += 1
        print(f"[{i}/{len(tickers)}] {et} -> {slug}  OK", flush=True)

    print(f"\nDone. resolved: {resolved}/{len(tickers)}. unresolved: {len(unresolved)} {unresolved}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
