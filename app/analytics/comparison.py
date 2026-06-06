"""Multi-stock comparison analytics.

This module contains pure functions that transform a close-price DataFrame
into the various derived views used by the dashboard.
"""

from __future__ import annotations

import pandas as pd

from app.constants import TRADING_DAYS_PER_YEAR

TICKER_COL = "Ticker"


def calculate_returns(close_prices: pd.DataFrame) -> pd.DataFrame:
    """Daily percentage returns, first row filled with zero."""
    return close_prices.pct_change().fillna(0)


def cumulative_returns_period(returns: pd.DataFrame) -> pd.DataFrame:
    """Cumulative returns over time, expressed as percentages."""
    return (((1 + returns).cumprod() - 1) * 100).round(2)


def _ranking_frame(series: pd.Series, value_label: str) -> pd.DataFrame:
    """Convert a per-ticker series into a sorted ranking frame."""
    return (
        series.round(2)
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"index": TICKER_COL, series.name or 0: value_label})
    )


def cumulative_returns_ranking(returns: pd.DataFrame) -> pd.DataFrame:
    """Total cumulative return per ticker, sorted descending."""
    cumulative = (1 + returns).prod() - 1
    series = cumulative * 100
    series.name = "Cumulative Return"
    return _ranking_frame(series, "Cumulative Return")


def annualized_volatility(returns: pd.DataFrame) -> pd.DataFrame:
    """Annualized volatility per ticker, sorted descending."""
    series = (returns.std() * (TRADING_DAYS_PER_YEAR**0.5)) * 100
    series.name = "Annualized Volatility"
    return _ranking_frame(series, "Annualized Volatility")


def coefficient_variation(close_prices: pd.DataFrame) -> pd.DataFrame:
    """Coefficient of variation per ticker, sorted descending."""
    series = (close_prices.std() / close_prices.mean()) * 100
    series.name = "Coefficient Variation"
    return _ranking_frame(series, "Coefficient Variation")
