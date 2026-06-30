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
import os, re, time, gzip, shutil
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
GCC_SNAP = gcc_paths.SNAP_DIR
GCC_MARKETS = ("_SR_", "_AE_", "_QA_", "_KW_", "_OM_")

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


def _finances_html(tf: str) -> str | None:
    p = ENGINE_SNAP / f"ms_{tf}_finances.html"
    if p.exists():
        return p.read_text("utf-8", errors="ignore")
    if p.with_suffix(".html.gz").exists():
        return gzip.decompress(p.with_suffix(".html.gz").read_bytes()).decode("utf-8", "ignore")
    return None


def _verify(expected_name: str, isin: str, code: str, html: str | None) -> bool:
    """Confirm the scraped page is the expected company by NAME or Tadawul CODE.

    NOTE: ISIN is deliberately NOT used — company_master.json has wrong ISINs for
    several Saudi names (e.g. Mouwasat's listed ISIN is actually Wafrah's), so an
    ISIN gate let wrong companies through (resolution and verification both trusted
    the same bad ISIN). Name-tokens OR the numeric code in the <title> are reliable.
    """
    if not html:
        return False
    m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    title = m.group(1).strip() if m else ""
    if _toks(expected_name) & _toks(title):
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


def _place(tf: str):
    """Copy a verified name's lean snapshots from the engine dir into the repo."""
    GCC_SNAP.mkdir(parents=True, exist_ok=True)
    for page in ("finances", "calendar", "calendar_quarterly", "summary"):
        for ext in (".html", ".html.gz"):
            src = ENGINE_SNAP / f"ms_{tf}_{page}{ext}"
            if src.exists():
                shutil.copy2(src, GCC_SNAP / src.name)


def _clear_gcc_region():
    """Drop all GCC snapshots from the repo dir; only verified names are re-placed,
    so corrupt/stale files from prior runs cannot survive."""
    if not GCC_SNAP.exists():
        return
    for f in GCC_SNAP.iterdir():
        if f.is_file() and any(m in f.name for m in GCC_MARKETS):
            try: f.unlink()
            except Exception: pass


def main() -> int:
    master = _master()
    tickers = list(dict.fromkeys(engine_ticker(yh) for yh, _b in MAP.values()))
    print(f"Refreshing MS snapshots for {len(tickers)} GCC names (scrape-then-verify)\n", flush=True)

    _clear_gcc_region()  # repo dir is rebuilt from verified names only
    resolved, unresolved = 0, []
    for i, et in enumerate(tickers, 1):
        rec = master.get(et) or {}
        name = rec.get("company_name") or FALLBACK_NAMES.get(et, "")
        code = et.split(".")[0]
        tf = et.replace(".", "_")
        if not name and not rec:
            print(f"[{i}/{len(tickers)}] {et}: NO name/record — skip", flush=True)
            unresolved.append(et); continue

        isin = (rec.get("isin") or "").strip()
        hit = None
        for slug in _candidate_slugs(et, rec, name):
            base = f"https://www.marketscreener.com/quote/stock/{slug}"
            prefix = f"ms_{tf}_{isin or 'noisin'}_{slug}"
            try:
                fetch_financial_forecast_series(base, cache_key_prefix=prefix)
            except Exception:
                pass
            time.sleep(PAGE_DELAY)
            if _verify(name, isin, code, _finances_html(tf)):
                hit = (slug, base, prefix); break

        if not hit:
            print(f"[{i}/{len(tickers)}] {et}: UNRESOLVED", flush=True)
            unresolved.append(et); continue

        slug, base, prefix = hit
        for fn in (fetch_calendar_events, fetch_summary_page):
            try: fn(base, cache_key_prefix=prefix)
            except Exception: pass
            time.sleep(PAGE_DELAY)
        _place(tf)  # copy ONLY this verified name's lean files into the repo
        resolved += 1
        print(f"[{i}/{len(tickers)}] {et} -> {slug}  OK", flush=True)

    print(f"\nDone. resolved: {resolved}/{len(tickers)}. unresolved: {len(unresolved)} {unresolved}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
