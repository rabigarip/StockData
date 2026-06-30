"""Verify each MS finances snapshot actually contains the expected company.

resolve_marketscreener_by_isin returns fuzzy search hits, so an ISIN-resolved
snapshot can hold the wrong company's financials. This reads the company name
out of each snapshot's <title> and token-matches it against company_master.
Anything that doesn't match is corrupt and must be rejected + re-resolved.
"""
from __future__ import annotations
import json, re, gzip
from pathlib import Path
import gcc_paths
from engine_data import _master, engine_ticker
from ticker_map import MAP

SNAP = gcc_paths.SNAP_DIR
# Names not in company_master — expected names for the title check (mirror refresh_snapshots).
FALLBACK_NAMES = {
    "NBK.KW": "National Bank of Kuwait", "ZAIN.KW": "Mobile Telecommunications Zain",
    "MABANEE.KW": "Mabanee", "EMIRATESNBD.AE": "Emirates NBD",
    "ADIB.AE": "Abu Dhabi Islamic Bank", "EMAARDEV.AE": "Emaar Development",
    "SALIK.AE": "Salik",
}
STOP = {"the","company","co","for","and","plc","pjsc","saog","group","sa","ltd",
        "public","joint","stock","cooperative","insurance","limited","bank","com",
        "holding","corporation","corp","services","industries","industry"}

def _toks(s):
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if w not in STOP and len(w) > 2}

def _title(ticker_form: str) -> str | None:
    base = SNAP / f"ms_{ticker_form}_finances.html"
    raw = None
    if base.exists():
        raw = base.read_text("utf-8", errors="ignore")
    elif base.with_suffix(".html.gz").exists():
        raw = gzip.decompress(base.with_suffix(".html.gz").read_bytes()).decode("utf-8","ignore")
    if not raw:
        return None
    m = re.search(r"<title>(.*?)</title>", raw, re.I | re.S)
    return m.group(1).strip() if m else ""

def main():
    master = _master()
    ok, bad, missing = [], [], []
    for yh, _blind in MAP.values():
        et = engine_ticker(yh)
        tf = et.replace(".", "_")
        expected = (master.get(et) or {}).get("company_name", "") or FALLBACK_NAMES.get(et, "")
        title = _title(tf)
        if title is None:
            missing.append(et); continue
        # match if expected name tokens overlap title, OR the ticker code is in the title
        code = et.split(".")[0]
        overlap = _toks(expected) & _toks(title)
        if overlap or (code.isdigit() and re.search(rf"\b{code}\b", title)):
            ok.append(et)
        else:
            bad.append((et, expected, title[:55]))
    print(f"VERIFIED OK: {len(ok)}   CORRUPT: {len(bad)}   NO SNAPSHOT: {len(missing)}\n")
    print("CORRUPT (snapshot holds the wrong company):")
    for et, exp, title in bad:
        print(f"  {et:14} expect '{exp[:30]}'  got '{title}'")
    print(f"\nNO SNAPSHOT ({len(missing)}): {missing}")
    return ok, bad, missing

if __name__ == "__main__":
    main()
