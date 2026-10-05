"""Tests for frozen domain models."""

import dataclasses

import pandas as pd
from app.models import ComparisonResult, StockStatistics, TickerInfo


def test_ticker_info_frozen() -> None:
    """TickerInfo is frozen and holds fields."""
    info = TickerInfo(
        ticker='PETR4.SA',
        last_price=10.0,
        previous_close=9.5,
        pct_today=5.26,
        open_price=9.8,
        day_high=10.2,
        day_low=9.7,
        long_name='Petrobras',
        summary='Oil company.',
        web_site='https://example.com',
        sector='Energy',
        industry='Oil',
    )
    assert dataclasses.is_dataclass(info)
    assert info.ticker == 'PETR4.SA'
    try:
        object.__setattr__  # noqa: B018
        info.ticker = 'X'  # type: ignore[misc]
        raise AssertionError('should be frozen')
    except dataclasses.FrozenInstanceError:
        pass


def test_stock_statistics_fields() -> None:
    """StockStatistics holds eight metrics."""
    stats = StockStatistics(
        volatility=1.0,
        cumulative_return=2.0,
        high_price=3.0,
        low_price=4.0,
        median_price=5.0,
        mean_price=6.0,
        standard_deviation=7.0,
        coefficient_variation=8.0,
    )
    assert stats.volatility == 1.0
    assert stats.coefficient_variation == 8.0


def test_comparison_result_bundles_frames() -> None:
    """ComparisonResult bundles dataframes."""
    frame = pd.DataFrame({'A': [1.0]})
    result = ComparisonResult(
        close_prices=frame,
        returns=frame,
        cumulative_returns_period=frame,
        cumulative_returns_ranking=frame,
        correlation_matrix=frame,
        annualized_volatility=frame,
        coefficient_variation=frame,
    )
    assert result.close_prices.equals(frame)
    assert result.correlation_matrix.equals(frame)
