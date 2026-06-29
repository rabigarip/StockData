"""Column map for 'Stock Financial Data - GCC.xlsx' (header row = row 2).

Each scraped column declares: the spreadsheet column letter, a human label,
and how it's sourced. The refresh script reads this to know what to write
where, and how to colour-code provenance. Columns A-F (ticker..Average Cost)
are owned by the maintainer's master and are NEVER written here.
"""

# period_label values come straight from the engine's FinancialPeriod:
#   quarterly -> "2025-Q1", annual -> "FY2024"

# Market / ratio block — all from fetch_quote()
QUOTE_COLS = {
    "G":  ("Market Price",      "price"),
    "AK": ("P/E",               "trailing_pe"),
    "AL": ("P/BV",              "price_to_book"),
    "AM": ("Div. Yield",        "dividend_yield_pct"),   # decimal -> %
    "AN": ("Dividend Per Share","dps"),                  # computed: yield*price (fallback)
}

# Derived from 1Y price history in the quote
HISTORY_COLS = {
    "H": ("31 Dec 2025 Price", "2025-12-31"),  # close on/just before this date
    "I": ("YTD Price Change",  "ytd"),          # vs 2025-12-31 close
    "J": ("QTD Price Change",  "qtd"),          # vs prior quarter-end close
}

# Reported actuals — from fetch_financials(); key = engine period_label
REVENUE_ACTUAL_COLS = {
    "K": "2025-Q1", "L": "2025-Q2", "M": "2025-Q3", "N": "2025-Q4", "O": "2026-Q1",
    "V": "FY2025",  "W": "FY2024",
}
NETPROFIT_ACTUAL_COLS = {
    "X": "2025-Q1", "Y": "2025-Q2", "Z": "2025-Q3", "AA": "2025-Q4", "AB": "2026-Q1",
    "AI": "FY2025", "AJ": "FY2024",
}

# Forward consensus — Phase 4 (MarketScreener/TradingView). Listed so the
# writer can flag them 'pending' rather than leave them silently blank.
REVENUE_ESTIMATE_COLS = {
    "P": "2026-Q2", "Q": "2026-Q3", "R": "2026-Q4",
    "S": "FY2026",  "T": "FY2027",  "U": "FY2028",
}
NETPROFIT_ESTIMATE_COLS = {
    "AC": "2026-Q2", "AD": "2026-Q3", "AE": "2026-Q4",
    "AF": "FY2026",  "AG": "FY2027",  "AH": "FY2028",
}
