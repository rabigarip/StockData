"""GCC market indices — Bloomberg ticker -> sourcing.

Tuple: (display_name, market, yahoo_symbol, investing_slug, tv_symbol).
Exactly one source field is set per index; the rest are None. The two with no
field set (MSMTR, SPGGCDT) have no free web source and come from manual_indices.json.
REFERENCE holds user-provided levels (2026-06-29) used to sanity-check scrapes.
"""

INDICES = {
    "SASEIDX": ("Tadawul All Share (TASI)", "Saudi Arabia",     "^TASI.SR", None,                      None),
    "DFMGI":   ("DFM General Index",         "UAE – Dubai",      "DFMGI.AE", None,                      None),
    "ADSMI":   ("ADX General Index",         "UAE – Abu Dhabi",  None,       "adx-general",             None),
    "QEAS":    ("QE All Share Index",        "Qatar",            None,       "qe-all-shares",           None),
    "KWSEAS":  ("Kuwait All Share Index",    "Kuwait",           None,       "kuwait-parallel-market",  None),
    "BHSEASI": ("Bahrain All Share Index",   "Bahrain",          None,       None,                      "BAHRAIN:BHBX"),
    # No free source -> manual_indices.json
    "MSMTR":   ("MSX 30 / Muscat (TR)",      "Oman",             None,       None,                      None),
    "SPGGCDT": ("S&P GCC Composite",         "GCC",              None,       None,                      None),
}

REFERENCE = {
    "SASEIDX": 10792.15, "DFMGI": 5993.35, "ADSMI": 9839.47, "QEAS": 4026.18,
    "KWSEAS": 8750.69, "BHSEASI": 2040.07, "MSMTR": 11549.59, "SPGGCDT": 316.81,
}
