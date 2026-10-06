"""Single-stock view."""

from __future__ import annotations

import pandas as pd
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
    """Show single-ticker analysis."""
    left_col, right_col = st.columns([0.25, 0.75])
    with left_col:
        period, ticker, info = _render_controls()
        if info is None:
            st.warning('Yahoo data temporarily unavailable. Try another ticker or period.')
            return
        try:
            history = fetch_history(ticker, period)
        except Exception:
            history = None
        if history is None or not isinstance(history, pd.DataFrame) or history.empty:
            st.warning('Yahoo data temporarily unavailable. Try another period.')
            return
        stats = calculate_statistics(history)
        render_statistics(stats)
    with right_col:
        if info is None:
            st.warning('Yahoo data temporarily unavailable. Try another ticker or period.')
            return
        if history is None or not isinstance(history, pd.DataFrame) or history.empty:
            st.warning('Yahoo data temporarily unavailable. Try another period.')
            return
        render_ticker_metrics(info)
        render_price_chart(history)


def _render_controls() -> tuple[str, str, TickerInfo | None]:
    """Show selectors and return picks."""
    with st.container(border=True, width='stretch', height='content'):
        period = st.pills(
            'Period',
            options=PERIODS,
            selection_mode='single',
            default=DEFAULT_PERIOD,
            key='single_period',
        )
        ticker = st.selectbox('Stock Ticker', options=STOCKS)
        info: TickerInfo | None
        try:
            info = fetch_ticker_info(ticker)
        except Exception:
            info = None
        if info is not None:
            render_about(info)
        else:
            st.warning('Yahoo data temporarily unavailable. Please retry shortly.')
    return period or DEFAULT_PERIOD, ticker, info
