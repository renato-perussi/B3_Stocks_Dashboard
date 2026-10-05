"""Tests for multi-stock comparison analytics."""

import pandas as pd
from app.analytics import comparison
from app.constants import TRADING_DAYS_PER_YEAR


def _closes() -> pd.DataFrame:
    """Two-ticker close fixture."""
    return pd.DataFrame(
        {
            'PETR4.SA': [10.0, 11.0, 12.0, 12.5],
            'VALE3.SA': [20.0, 19.0, 21.0, 22.0],
        }
    )


def test_calculate_returns_zero_fills_first_row() -> None:
    """First return row is zero."""
    out = comparison.calculate_returns(_closes())
    assert out.iloc[0].tolist() == [0.0, 0.0]
    assert out.shape == (4, 2)


def test_cumulative_returns_period_formula() -> None:
    """Cumulative matches cumprod formula."""
    closes = _closes()
    returns = comparison.calculate_returns(closes)
    out = comparison.cumulative_returns_period(returns)
    expected = (((1 + returns).cumprod() - 1) * 100).round(2)
    pd.testing.assert_frame_equal(out, expected)


def test_rankings_sorted_descending() -> None:
    """Rankings are sorted descending."""
    returns = comparison.calculate_returns(_closes())
    for frame in [
        comparison.cumulative_returns_ranking(returns),
        comparison.annualized_volatility(returns),
        comparison.coefficient_variation(_closes()),
    ]:
        assert 'Ticker' in frame.columns
        values = frame.iloc[:, 1].tolist()
        assert values == sorted(values, reverse=True)


def test_annualized_volatility_formula() -> None:
    """Volatility uses sqrt 252 scale."""
    returns = comparison.calculate_returns(_closes())
    out = comparison.annualized_volatility(returns)
    expected = (returns.std() * (TRADING_DAYS_PER_YEAR**0.5)) * 100
    assert out.iloc[0, 1] == round(expected.max(), 2)


def test_coefficient_variation_formula() -> None:
    """CV matches std over mean."""
    closes = _closes()
    out = comparison.coefficient_variation(closes)
    assert set(out['Ticker'].tolist()) == {'PETR4.SA', 'VALE3.SA'}
