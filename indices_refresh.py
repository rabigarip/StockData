"""Write GCC index last-prices to a separate workbook: 'GCC Indices.xlsx'.

All sources run locally (no GitHub Action needed for indices):
  - Yahoo:     TASI, DFM (live)
  - Investing: ADX General (live; Investing isn't IP-blocked like MarketScreener)
  - Manual:    the 5 Bloomberg-only indices (read from manual_indices.json, which
               you update from Bloomberg; the refresh preserves them)

Colour: green = live (Yahoo/Investing), amber = manual, red = unavailable.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

import openpyxl
from openpyxl.styles import PatternFill, Font
import yfinance as yf

import indices_config as IC
from refresh_index_snapshots import _fetch_last  # live Investing scrape

HERE = Path(__file__).resolve().parent
OUT = HERE / "GCC Indices.xlsx"
MANUAL = HERE / "manual_indices.json"

GREEN = PatternFill("solid", fgColor="C6EFCE")
AMBER = PatternFill("solid", fgColor="FFEB9C")
RED   = PatternFill("solid", fgColor="FFC7CE")


def _yahoo_last(sym: str):
    try:
        c = yf.Ticker(sym).history(period="5d")["Close"].dropna()
        return round(float(c.iloc[-1]), 2) if not c.empty else None
    except Exception:
        return None


def main():
    manual = json.loads(MANUAL.read_text()) if MANUAL.exists() else {}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Indices"
    ws.append(["Bloomberg Ticker", "Index", "Market", "Last Price", "As of", "Source"])
    for c in ws[1]:
        c.font = Font(bold=True)

    for bbg, (name, market, ysym, slug) in IC.INDICES.items():
        last = asof = None; source = "unavailable"; fill = RED
        if ysym:
            last = _yahoo_last(ysym)
            if last is not None: source, asof, fill = "Yahoo", today, GREEN
        elif slug:
            v, _page = _fetch_last(slug)
            ref = IC.REFERENCE.get(bbg)
            if v is not None and ref and 0.5 * ref <= v <= 2 * ref:
                last, source, asof, fill = round(v, 2), "Investing", today, GREEN
        elif bbg in manual:
            last = manual[bbg].get("last"); asof = manual[bbg].get("asof")
            if last is not None: source, fill = "Manual (Bloomberg)", AMBER
        ws.append([bbg, name, market, last, asof, source])
        ws.cell(row=ws.max_row, column=4).fill = fill

    for col, w in zip("ABCDEF", (16, 26, 18, 12, 12, 18)):
        ws.column_dimensions[col].width = w
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ws.append([]); ws.append([f"Last refreshed: {stamp}"])
    wb.save(OUT)
    priced = sum(1 for r in range(2, 2 + len(IC.INDICES)) if ws.cell(row=r, column=4).value is not None)
    print(f"Wrote {OUT}  ({priced}/{len(IC.INDICES)} indices priced)")


if __name__ == "__main__":
    main()
