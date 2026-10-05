"""Single stock view."""

from __future__ import annotations

import streamlit as st

from app.analytics.statistics import calculate_statistics
from app.config import PERIODS, STOCKS
from app.constants import DEFAULT_PERIOD
from app.data.yfinance_client import fetch_history, fetch_ticker_info
from app.errors import handle_data_errors
from app.models import TickerInfo
from app.ui.components.about_popover import render_about
from app.ui.components.price_chart import render_price_chart
from app.ui.components.statistics_panel import render_statistics
from app.ui.components.ticker_metrics_row import render_ticker_metrics


@handle_data_errors('single stock view')
def render_single_stock_view() -> None:
    """Show one ticker analysis."""
    left_col, right_col = st.columns([0.25, 0.75])
    with left_col:
        period, ticker, info = _render_controls()
        history = fetch_history(ticker, period)
        stats = calculate_statistics(history)
        render_statistics(stats)
    with right_col:
        render_ticker_metrics(info)
        render_price_chart(history)


def _render_controls() -> tuple[str, str, TickerInfo]:
    """Show picks and return them."""
    with st.container(border=True, width='stretch', height='content'):
        period = st.pills(
            'Period',
            options=PERIODS,
            selection_mode='single',
            default=DEFAULT_PERIOD,
            key='single_period',
        )
        ticker = st.selectbox('Stock Ticker', options=STOCKS)
        info = fetch_ticker_info(ticker)
        render_about(info)
    return period or DEFAULT_PERIOD, ticker, info
