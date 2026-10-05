"""Selectors for comparison view."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from app.config import PERIODS, STOCKS, STOCKS_DEFAULT
from app.constants import DEFAULT_PERIOD


@dataclass(frozen=True)
class ComparisonSelection:
    """User picks for compare view."""

    period: str
    tickers: list[str]


def render_comparison_controls() -> ComparisonSelection:
    """Show period and ticker picks."""
    with st.container(border=True, width='stretch', height='content'):
        period = st.pills(
            'Period',
            options=PERIODS,
            selection_mode='single',
            default=DEFAULT_PERIOD,
            key='comparison_period',
        )
        tickers = st.multiselect(
            'Stock Tickers',
            options=STOCKS,
            default=STOCKS_DEFAULT,
        )
        st.caption(
            'Select at least two or more stocks to analyze Cumulative Returns, '
            'Correlations, and Volatility Metrics.'
        )
    return ComparisonSelection(period=period or DEFAULT_PERIOD, tickers=tickers)
