# GCC Sheet Autoupdate

Auto-populates `Stock Financial Data - GCC.xlsx` by reusing the `final_earnings`
engine as the data layer. Writes only columns **G–AN**; **A–F** (incl. Average
Cost) are never touched.

## Files
- `ticker_map.py` — 60 Bloomberg → Yahoo symbols (name-verified)
- `column_map.py` — which engine field feeds which spreadsheet column
- `engine_data.py` — joins names to the engine's `company_master.json` (ISIN, MS id)
- `gcc_refresh.py` — the writer (Yahoo market/actuals + MarketScreener estimates)
- `ms_estimates.py` — forward estimates via the engine's MarketScreener scraper
- `verify_map.py` — checks every Yahoo symbol resolves to the right company
- `run_autoupdate.sh` — one-command refresh

## Provenance colours (in the populated file)
- 🟩 green — live actual
- 🟨 amber — computed / derived
- 🟦 blue — estimate pending (fills on Render)
- 🟥 red — missing / needs MarketScreener fallback (blind UAE/Oman)

## Test it on your machine (now)
```bash
cd ~/gcc-data-refresh
./run_autoupdate.sh
open "Stock Financial Data - GCC (populated).xlsx"
```
**What you'll see locally:** market data, ratios, and reported actuals fill for
the 45 Yahoo-covered names (Saudi/Qatar/Kuwait). Estimates and the 15 blind
UAE/Oman names stay flagged — MarketScreener blocks residential/Mac IPs, so those
fill only on Render.

## Full coverage — estimates, blind names, bank backfill (MarketScreener)

Forward estimates (annual **and** quarterly), the blind UAE/Oman names, and the
bank-actual gaps all come from one source: the MarketScreener **/finances/**
forecast page, parsed by `ms_forecast.py`.

**Key fact:** MarketScreener Cloudflare-blocks BOTH residential Macs AND Render
datacenter IPs. The engine scrapes it from **GitHub Actions** runners (residential-
class IPs), which commit HTML snapshots to `final_earnings/data/marketscreener/`.
`gcc_refresh.py` reads those committed snapshots locally — **no live fetch, no block.**

So coverage = "does this name have a committed finances snapshot?":
- Names already snapshotted → estimates/blind/backfill fill immediately, anywhere.
- To add the rest → add them to the GitHub Actions workflow
  `final_earnings/.github/workflows/refresh-marketscreener-cache.yml` (resolves slug
  from the ISIN already in `company_master.json`), let it run, commit snapshots.

**Daily refresh:** `gcc_refresh.py` reads Yahoo (prices/actuals) live + MS snapshots
from the repo. Runs anywhere — Render or a local cron. The MS snapshots refresh on
their own GitHub Actions schedule.

## Delivery to OneDrive
Render writes the populated file to the shared location. Recommended path on a
locked-down work tenant: a **Power Automate flow you own** (email the file from
Render → flow saves it to work OneDrive). Recipient opens a **view-only** master
and makes throwaway copies to edit.
```
