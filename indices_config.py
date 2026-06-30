"""GCC market indices — Bloomberg ticker -> (name, market, yahoo symbol or None).

Yahoo covers TASI and DFM; the other six are Yahoo-blind and come from an
Investing.com snapshot scraped by the GitHub Action (same pattern as the blind
stocks). REFERENCE holds user-provided levels (2026-06-29) used to sanity-check
the scraped values.
"""

# bloomberg : (display_name, market, yahoo_symbol_or_None, investing_slug_or_None)
INDICES = {
    "SASEIDX": ("Tadawul All Share (TASI)", "Saudi Arabia",     "^TASI.SR", None),
    "DFMGI":   ("DFM General Index",         "UAE – Dubai",  "DFMGI.AE", None),
    "ADSMI":   ("ADX General Index",         "UAE – Abu Dhabi", None,    "adx-general"),
    # No free web source (Bloomberg-specific All-Share / TR variants) -> manual_indices.json
    "QEAS":    ("QE All Share Index",        "Qatar",            None,       None),
    "KWSEAS":  ("Kuwait All Share Index",    "Kuwait",           None,       None),
    "BHSEASI": ("Bahrain All Share Index",   "Bahrain",          None,       None),
    "MSMTR":   ("MSX 30 / Muscat",           "Oman",             None,       None),
    "SPGGCDT": ("S&P GCC Composite",         "GCC",              None,       None),
}

# User-provided reference levels (2026-06-29) — verification gate for scraped values.
REFERENCE = {
    "SASEIDX": 10792.15, "DFMGI": 5993.35, "ADSMI": 9839.47, "QEAS": 4026.18,
    "KWSEAS": 8750.69, "BHSEASI": 2040.07, "MSMTR": 11549.59, "SPGGCDT": 316.81,
}
