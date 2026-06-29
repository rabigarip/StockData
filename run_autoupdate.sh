#!/usr/bin/env bash
# GCC sheet autoupdate — one command. Refreshes the populated workbook.
#
#   Local (your Mac):  fills market + ratios + reported actuals (Yahoo).
#                      Estimates + blind UAE/Oman flagged pending (MS blocks
#                      this IP — those fill when run on Render).
#   Render:            additionally fills estimates + blind names from the
#                      warm MarketScreener cache.
#
# Usage:  ./run_autoupdate.sh
set -euo pipefail

ENGINE=/Users/rabigaarip/final_earnings
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "[$(date '+%H:%M:%S')] GCC autoupdate starting..."
PYTHONPATH="$ENGINE" "$ENGINE/.venv/bin/python" "$HERE/gcc_refresh.py"
echo "[$(date '+%H:%M:%S')] Done. Open: $HERE/Stock Financial Data - GCC (populated).xlsx"
