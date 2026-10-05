"""Pure multi-stock comparison helpers."""

from __future__ import annotations

import pandas as pd

from app.constants import TRADING_DAYS_PER_YEAR

TICKER_COL = 'Ticker'


def calculate_returns(close_prices: pd.DataFrame) -> pd.DataFrame:
    """Daily returns with first row zero."""
    return close_prices.pct_change().fillna(0)


def cumulative_returns_period(returns: pd.DataFrame) -> pd.DataFrame:
    """Cumulative returns in percent."""
    return (((1 + returns).cumprod() - 1) * 100).round(2)


def _ranking_frame(series: pd.Series, value_label: str) -> pd.DataFrame:
    """Sort series into ranking frame."""
    return (
        series.round(2)
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={'index': TICKER_COL, series.name or 0: value_label})
    )


def cumulative_returns_ranking(returns: pd.DataFrame) -> pd.DataFrame:
    """Total return per ticker sorted."""
    cumulative = (1 + returns).prod() - 1
    series = cumulative * 100
    series.name = 'Cumulative Return'
    return _ranking_frame(series, 'Cumulative Return')


def annualized_volatility(returns: pd.DataFrame) -> pd.DataFrame:
    """Yearly volatility per ticker sorted."""
    series = (returns.std() * (TRADING_DAYS_PER_YEAR**0.5)) * 100
    series.name = 'Annualized Volatility'
    return _ranking_frame(series, 'Annualized Volatility')


def coefficient_variation(close_prices: pd.DataFrame) -> pd.DataFrame:
    """Variation coefficient per ticker sorted."""
    series = (close_prices.std() / close_prices.mean()) * 100
    series.name = 'Coefficient Variation'
    return _ranking_frame(series, 'Coefficient Variation')
