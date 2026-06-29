"""Verify each non-blind Yahoo symbol resolves to the company the sheet expects.

For every mapped ticker, fetch Yahoo's name and token-compare against the
sheet's Stock Name. Catches wrong Tadawul codes before they pull bad data.
"""
from __future__ import annotations
import re, openpyxl
from src.providers.yahoo import validate_ticker
import ticker_map as TM

SRC = "/Users/rabigaarip/Downloads/Stock Financial Data - GCC.xlsx"
STOP = {"the","company","co","for","and","plc","pjsc","saog","group","sa","ltd",
        "public","joint","stock","cooperative","insurance","limited","bank","com"}

def toks(s):
    return {w for w in re.findall(r"[a-z]+", (s or "").lower()) if w not in STOP and len(w) > 2}

def main():
    wb = openpyxl.load_workbook(SRC, data_only=True); ws = wb["Sheet1"]
    sheet_name = {ws.cell(row=r, column=1).value: ws.cell(row=r, column=2).value
                  for r in range(3, ws.max_row + 1)}
    ok = mismatch = blind = unresolved = 0
    for bbg, (yh, is_blind) in TM.MAP.items():
        want = sheet_name.get(bbg, "")
        if is_blind:
            blind += 1; continue
        info = validate_ticker(yh)
        if not info or not info.get("name"):
            print(f"  UNRESOLVED  {bbg:<20} {yh:<10} (no Yahoo data) — want: {want}")
            unresolved += 1; continue
        got = info["name"]
        overlap = toks(want) & toks(got)
        if overlap:
            ok += 1
            # print(f"  OK          {bbg:<20} {yh:<10} {got}")
        else:
            print(f"  MISMATCH    {bbg:<20} {yh:<10} got '{got}'  != want '{want}'")
            mismatch += 1
    print(f"\nOK={ok}  MISMATCH={mismatch}  UNRESOLVED={unresolved}  BLIND(skipped)={blind}")

if __name__ == "__main__":
    main()
