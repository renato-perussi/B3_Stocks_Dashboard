"""Domain models for analytics and UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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

    @classmethod
    def from_raw(cls, ticker: str, raw: dict[str, Any]) -> TickerInfo:
        """Build TickerInfo from partial dict."""

        def _num(key: str, default: float) -> float:
            """Parse float or default."""
            try:
                value = raw.get(key, default)
                if value is None:
                    return default
                parsed = float(value)
                if parsed != parsed or parsed in (float('inf'), float('-inf')):
                    return default
                return parsed
            except (TypeError, ValueError, OverflowError):
                return default

        def _str(key: str, default: str = '') -> str:
            value = raw.get(key, default)
            return str(value) if value is not None else default

        last = _num('last_price', float('nan'))
        previous = _num('previous_close', float('nan'))
        if last != last or previous != previous:  # Require valid price.
            raise ValueError(f'Incomplete quote data for {ticker}.')
        pct = 0.0 if previous == 0 else (last / previous - 1) * 100
        return cls(
            ticker=ticker,
            last_price=round(last, 2),
            previous_close=round(previous, 2),
            pct_today=float(_num('pct_today', pct)),
            open_price=round(_num('open_price', last), 2),
            day_high=round(_num('day_high', last), 2),
            day_low=round(_num('day_low', last), 2),
            long_name=_str('long_name', ticker),
            summary=_str('summary'),
            web_site=_str('web_site'),
            sector=_str('sector'),
            industry=_str('industry'),
        )


@dataclass(frozen=True)
class StockStatistics:
    """Period stats for one stock."""

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
    """Frames for multi-stock view."""

    close_prices: pd.DataFrame
    returns: pd.DataFrame
    cumulative_returns_period: pd.DataFrame
    cumulative_returns_ranking: pd.DataFrame
    correlation_matrix: pd.DataFrame
    annualized_volatility: pd.DataFrame
    coefficient_variation: pd.DataFrame
