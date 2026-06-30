"""Live index price fetchers — all work from a normal IP (no GitHub Action needed).

  investing_last(slug)  -> Investing.com /indices/<slug>  (data-test price element)
  tv_last(symbol)       -> TradingView scanner quote (EXCHANGE:SYMBOL)
"""
from __future__ import annotations
from curl_cffi import requests as creq
from bs4 import BeautifulSoup

_TV_HDR = {"Origin": "https://www.tradingview.com", "Referer": "https://www.tradingview.com/"}


def investing_last(slug: str):
    """(last_price, page_name) from an Investing.com index page, or (None, msg)."""
    try:
        r = creq.get(f"https://www.investing.com/indices/{slug}", impersonate="chrome", timeout=25)
    except Exception as e:
        return None, f"ERR {type(e).__name__}"
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    soup = BeautifulSoup(r.text, "lxml")
    el = soup.select_one('[data-test="instrument-price-last"]')
    name = (soup.find("h1").get_text(strip=True) if soup.find("h1") else "")
    if not el:
        return None, name or "no-price-element"
    try:
        return float(el.get_text(strip=True).replace(",", "")), name
    except ValueError:
        return None, name


def tv_last(symbol: str):
    """Last close from TradingView for EXCHANGE:SYMBOL, or None."""
    u = f"https://scanner.tradingview.com/symbol?symbol={symbol.replace(':', '%3A')}&fields=close&no_404=true"
    try:
        return creq.get(u, impersonate="chrome", headers=_TV_HDR, timeout=20).json().get("close")
    except Exception:
        return None
