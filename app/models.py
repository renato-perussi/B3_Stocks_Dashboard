"""Domain models used across analytics and UI layers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TickerInfo:
    """Real-time quote and fundamental company information."""

    ticker: str
    last_price: float
    previous_close: float
    pct_today: float
    open_price: float
    day_high: float
    day_low: float
    long_name: str
    summary: str
    web_site: str
    sector: str
    industry: str


@dataclass(frozen=True)
class StockStatistics:
    """Statistical metrics computed from a single stock's price history."""

    volatility: float
    cumulative_return: float
    high_price: float
    low_price: float
    median_price: float
    mean_price: float
    standard_deviation: float
    coefficient_variation: float


@dataclass(frozen=True)
class ComparisonResult:
    """Bundle of all dataframes produced for a multi-stock comparison."""

    close_prices: pd.DataFrame
    returns: pd.DataFrame
    cumulative_returns_period: pd.DataFrame
    cumulative_returns_ranking: pd.DataFrame
    correlation_matrix: pd.DataFrame
    annualized_volatility: pd.DataFrame
    coefficient_variation: pd.DataFrame
