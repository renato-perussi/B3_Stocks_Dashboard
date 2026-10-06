"""Tests for statistics analytics."""

import pandas as pd
import pytest
from app.analytics.statistics import calculate_statistics
from app.constants import TRADING_DAYS_PER_YEAR
from app.data.exceptions import DataUnavailableError
from app.models import StockStatistics


def _history() -> pd.DataFrame:
    """Small OHLC history fixture."""
    return pd.DataFrame(
        {
            'Close': [100.0, 105.0, 110.0, 108.0],
            'High': [101.0, 106.0, 111.0, 109.0],
            'Low': [99.0, 104.0, 109.0, 107.0],
        }
    )


def test_calculate_statistics_values() -> None:
    """Stats match manual formulas."""
    history = _history()
    stats = calculate_statistics(history)
    assert isinstance(stats, StockStatistics)
    assert stats.high_price == 111.0
    assert stats.low_price == 99.0
    assert stats.median_price == history['Close'].median()
    assert stats.mean_price == history['Close'].mean()
    returns = history['Close'].pct_change().fillna(0)
    expected_vol = returns.std() * (TRADING_DAYS_PER_YEAR**0.5) * 100
    assert stats.volatility == expected_vol
    expected_cum = ((1 + returns).prod() - 1) * 100
    assert stats.cumulative_return == expected_cum


def test_calculate_statistics_cv() -> None:
    """CV equals std over mean in percent."""
    stats = calculate_statistics(_history())
    assert stats.coefficient_variation == (stats.standard_deviation / stats.mean_price) * 100


def test_calculate_statistics_missing_high_raises() -> None:
    """Date/Close-only frame raises DataUnavailable."""
    frame = pd.DataFrame({'Date': ['2024-01-02', '2024-01-03'], 'Close': [10.0, 11.0]})
    with pytest.raises(DataUnavailableError):
        calculate_statistics(frame)


def test_normalize_history_requires_high_low() -> None:
    """_normalize_history validates High/Low early."""
    import app.data.yfinance_client as client

    idx = pd.DatetimeIndex([pd.Timestamp('2024-01-02'), pd.Timestamp('2024-01-03')])
    frame = pd.DataFrame({'Close': [10.0, 11.0]}, index=idx)
    frame.index.name = 'Date'
    with pytest.raises(DataUnavailableError):
        client._normalize_history(frame, 'PETR4.SA', '1mo')
