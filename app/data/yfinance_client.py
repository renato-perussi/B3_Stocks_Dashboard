"""yfinance data access layer.

This module is the only place in the application that talks to the yfinance
library. All network I/O is centralized here so it can be cached, mocked, or
swapped without touching the rest of the codebase.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st
import yfinance as yf

from app.constants import CACHE_TTL_INFO
from app.models import TickerInfo


@st.cache_data
def fetch_history(ticker: str, period: str) -> pd.DataFrame:
    """Fetch OHLCV history for a single ticker over ``period``.

    Returns a DataFrame with a ``Date`` column of Python ``date`` objects and
    numeric columns rounded to two decimals.
    """
    history = yf.Ticker(ticker).history(period=period)
    history = history.reset_index().round(2)
    history["Date"] = pd.to_datetime(history["Date"]).dt.date
    return history


@st.cache_data
def fetch_close_prices(period: str, tickers: list[str]) -> pd.DataFrame:
    """Fetch the close price series for multiple tickers aligned by date."""
    close_prices = pd.DataFrame()
    for ticker in tickers:
        ticker_history = yf.Ticker(ticker).history(period=period)
        close_prices[ticker] = ticker_history["Close"]
    return close_prices


@st.cache_data(ttl=CACHE_TTL_INFO)
def fetch_ticker_info(ticker: str) -> TickerInfo:
    """Fetch real-time quote and company profile for ``ticker``."""
    stock = yf.Ticker(ticker)

    last_price = round(stock.fast_info["lastPrice"], 2)
    previous_close = round(stock.info["previousClose"], 2)
    pct_today = (last_price / previous_close - 1) * 100
    open_price = round(stock.info["open"], 2)
    day_high = round(stock.info["dayHigh"], 2)
    day_low = round(stock.info["dayLow"], 2)

    return TickerInfo(
        ticker=ticker,
        last_price=last_price,
        previous_close=previous_close,
        pct_today=pct_today,
        open_price=open_price,
        day_high=day_high,
        day_low=day_low,
        long_name=stock.info["longName"],
        summary=stock.info["longBusinessSummary"],
        web_site=stock.info["website"],
        sector=stock.info["sector"],
        industry=stock.info["industry"],
    )
