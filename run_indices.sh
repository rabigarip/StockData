#!/usr/bin/env bash
# GCC indices only — quick standalone update (no engine, no stock sheet).
# Builds 'GCC Indices.xlsx' from Yahoo + Investing + TradingView (all live),
# preserving the manual entries in manual_indices.json.
#
# Usage:  ./run_indices.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-${ENGINE_ROOT:-$HOME/final_earnings}/.venv/bin/python}"

echo "[$(date '+%H:%M:%S')] Updating GCC indices..."
"$PY" "$HERE/indices_refresh.py"
echo "Open: $HERE/GCC Indices.xlsx"
