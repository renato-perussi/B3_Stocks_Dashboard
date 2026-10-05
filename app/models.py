"""Domain models for analytics and UI."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TickerInfo:
    """Quote and company profile."""

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
    """Per-period stats for one stock."""

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
    """All frames for multi-stock view."""

    close_prices: pd.DataFrame
    returns: pd.DataFrame
    cumulative_returns_period: pd.DataFrame
    cumulative_returns_ranking: pd.DataFrame
    correlation_matrix: pd.DataFrame
    annualized_volatility: pd.DataFrame
    coefficient_variation: pd.DataFrame
