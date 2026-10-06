"""Pure stats for one stock history."""

from __future__ import annotations

import pandas as pd

from app.constants import TRADING_DAYS_PER_YEAR
from app.data.exceptions import DataUnavailableError
from app.models import StockStatistics


def calculate_statistics(history: pd.DataFrame) -> StockStatistics:
    """Build stats from OHLC history."""
    if history is None or not isinstance(history, pd.DataFrame) or history.empty:
        raise DataUnavailableError('Empty history for statistics.')
    cols_lower: dict[str, str] = {str(c).lower(): str(c) for c in history.columns}
    for required in ('close', 'high', 'low'):
        if required not in cols_lower:
            raise DataUnavailableError(f'Missing {required.capitalize()} column for statistics.')
    close_col = cols_lower['close']
    high_col = cols_lower['high']
    low_col = cols_lower['low']
    returns = history[close_col].pct_change().fillna(0)
    volatility = returns.std() * (TRADING_DAYS_PER_YEAR**0.5) * 100
    cumulative_return = ((1 + returns).prod() - 1) * 100
    median_price = history[close_col].median()
    mean_price = history[close_col].mean()
    standard_deviation = history[close_col].std()
    coefficient_variation = (standard_deviation / mean_price) * 100
    high_price = history[high_col].max()
    low_price = history[low_col].min()
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
