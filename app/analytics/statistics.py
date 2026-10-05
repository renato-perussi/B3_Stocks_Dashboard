"""Pure stats for one stock history."""

from __future__ import annotations

import pandas as pd

from app.constants import TRADING_DAYS_PER_YEAR
from app.models import StockStatistics


def calculate_statistics(history: pd.DataFrame) -> StockStatistics:
    """Build stats from OHLC history."""
    returns = history['Close'].pct_change().fillna(0)
    volatility = returns.std() * (TRADING_DAYS_PER_YEAR**0.5) * 100
    cumulative_return = ((1 + returns).prod() - 1) * 100
    median_price = history['Close'].median()
    mean_price = history['Close'].mean()
    standard_deviation = history['Close'].std()
    coefficient_variation = (standard_deviation / mean_price) * 100
    high_price = history['High'].max()
    low_price = history['Low'].min()
    return StockStatistics(
        volatility=volatility,
        cumulative_return=cumulative_return,
        high_price=high_price,
        low_price=low_price,
        median_price=median_price,
        mean_price=mean_price,
        standard_deviation=standard_deviation,
        coefficient_variation=coefficient_variation,
    )
