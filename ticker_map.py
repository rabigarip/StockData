"""Bloomberg ticker -> Yahoo symbol map for the 60 GCC names.

Saudi (AB)  -> numeric Tadawul code + .SR
Qatar (QD)  -> alpha + .QA
Kuwait (KK) -> alpha + .KW
UAE (UH)    -> .AD (ADX) / .DU (DFM)  — Yahoo-blind, handled in Phase 3
Oman (OM)   -> .OM                    — Yahoo-blind, handled in Phase 3

`blind=True` rows are skipped by the Yahoo path and flagged red until the
Phase-3 fallback (engine's _yahoo_blind / MarketScreener) is wired in.
Every non-blind row is name-verified against the sheet by verify_map.py.
"""

# bloomberg_ticker : (yahoo_symbol, blind)
MAP = {
    # ── Saudi Arabia (.SR, numeric Tadawul codes) ──
    "RJHI AB Equity":   ("1120.SR", False),
    "SNB AB Equity":    ("1180.SR", False),
    "STC AB Equity":    ("7010.SR", False),
    "ALMARAI AB Equity":("2280.SR", False),
    "MAADEN AB Equity": ("1211.SR", False),
    "JARIR AB Equity":  ("4190.SR", False),
    "ARAMCO AB Equity": ("2222.SR", False),
    "TAWUNIYA AB Equity":("8010.SR", False),
    "RIBL AB Equity":   ("1010.SR", False),
    "SULAIMAN AB EQUITY":("4013.SR", False),
    "ALINMA AB Equity": ("1150.SR", False),
    "SAL AB Equity":    ("4263.SR", False),
    "SABB AB Equity":   ("1060.SR", False),
    "EEC AB Equity":    ("7020.SR", False),
    "ELM AB Equity":    ("7203.SR", False),
    "BSF AB Equity":    ("1050.SR", False),
    "ZAINKSA AB Equity":("7030.SR", False),
    "ALBI AB Equity":   ("1140.SR", False),
    "YACCO AB Equity":  ("3020.SR", False),
    "RASAN AB Equity":  ("8313.SR", False),
    "SABIC AB Equity":  ("2010.SR", False),
    "ACWA AB Equity":   ("2082.SR", False),
    "SAFCO AB Equity":  ("2020.SR", False),
    "ALDREES AB Equity":("4200.SR", False),
    "MOUWASAT AB EQUITY":("4002.SR", False),
    "MAHARAH AB EQUITY":("1831.SR", False),
    "LUBEREF AB Equity":("2223.SR", False),
    "RETAL AB Equity":  ("4322.SR", False),
    "ADES AB Equity":   ("2382.SR", False),
    "SECO AB Equity":   ("5110.SR", False),
    "BUPA AB Equity":   ("8210.SR", False),
    "SOLUTION AB Equity":("7202.SR", False),
    "ARABIANM AB EQUITY":("2284.SR", False),
    "EASTPIPE AB Equity":("1321.SR", False),
    "ALBABTAI AB Equity":("2320.SR", False),
    # ── Qatar (.QA) ──
    "QNBK QD Equity":   ("QNBK.QA", False),
    "QIBK QD Equity":   ("QIBK.QA", False),
    "ORDS QD Equity":   ("ORDS.QA", False),
    "CBQK QD Equity":   ("CBQK.QA", False),
    "MARK QD Equity":   ("MARK.QA", False),
    "QGTS QD Equity":   ("QGTS.QA", False),
    # ── Kuwait (.KW) ──
    "KFH KK Equity":    ("KFH.KW", False),
    "NBK KK Equity":    ("NBK.KW", False),
    "ZAIN KK Equity":   ("ZAIN.KW", False),
    "MABANEE KK Equity":("MABANEE.KW", False),
    # ── UAE (Yahoo-blind: .AD ADX / .DU DFM) ──
    "ADCB UH Equity":   ("ADCB.AD", True),
    "ADNOCLS UH Equity":("ADNOCLS.AD", True),
    "EMAAR UH Equity":  ("EMAAR.DU", True),
    "ALDAR UH Equity":  ("ALDAR.AD", True),
    "EMIRATES UH Equity":("EMIRATESNBD.DU", True),
    "FAB UH Equity":    ("FAB.AD", True),
    "ADNOCGAS UH Equity":("ADNOCGAS.AD", True),
    "ADIB UH Equity":   ("ADIB.AD", True),
    "ADNOCDRI UH Equity":("ADNOCDRILL.AD", True),
    "EMAARDEV UH Equity":("EMAARDEV.DU", True),
    "DIB UH EQUITY":    ("DIB.DU", True),
    "SALIK UH Equity":  ("SALIK.DU", True),
    # ── Oman (Yahoo-blind: .OM) ──
    "BKMB OM EQUITY":   ("BKMB.OM", True),
    "AACT OM Equity":   ("AACT.OM", True),
    "OQEP OM Equity":   ("OQEP.OM", True),
}
