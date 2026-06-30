#!/usr/bin/env bash
# GCC sheet autoupdate — one command, run on your Mac.
#
#   1. Pulls the latest MarketScreener snapshots (committed by the GitHub Action).
#   2. Fetches fresh prices/ratios/actuals from Yahoo (live).
#   3. Writes the populated workbook.
#
# Prices refresh every run; estimates are as fresh as the last snapshot Action.
#
# Usage:  ./run_autoupdate.sh   [then it prints the output path]
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ENGINE="${ENGINE_ROOT:-$HOME/final_earnings}"
MASTER="${GCC_MASTER_XLSX:-$HOME/Downloads/Stock Financial Data - GCC.xlsx}"
OUT="$HERE/Stock Financial Data - GCC (populated).xlsx"

echo "[$(date '+%H:%M:%S')] 1/2 Pulling latest MarketScreener snapshots..."
git -C "$HERE" fetch origin main -q 2>/dev/null \
  && git -C "$HERE" checkout origin/main -- data/marketscreener 2>/dev/null \
  && echo "      snapshots up to date" \
  || echo "      (offline or no update — using local snapshots)"

echo "[$(date '+%H:%M:%S')] 2/2 Building sheet from Yahoo (live) + snapshots..."
GCC_MASTER_XLSX="$MASTER" ENGINE_ROOT="$ENGINE" PYTHONPATH="$ENGINE" \
  "$ENGINE/.venv/bin/python" "$HERE/gcc_refresh.py"

echo "[$(date '+%H:%M:%S')] Done."
echo "Open:  $OUT"
