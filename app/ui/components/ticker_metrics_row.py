"""Horizontal metrics row showing real-time quote data for the selected ticker."""

from __future__ import annotations

import streamlit as st

from app.models import TickerInfo
from app.ui.formatters import format_brl, format_pct_signed


def render_ticker_metrics(info: TickerInfo) -> None:
    """Render the top-right metrics row (change %, last price, OHLC, etc.)."""
    weights = [0.16, 0.14, 0.14, 0.14, 0.14, 0.14, 0.14]
    cols = st.columns(weights, vertical_alignment="center")

    cols[0].markdown(f"## {info.ticker} ")
    cols[1].metric(label="Change %", value=format_pct_signed(info.pct_today))
    cols[2].metric(label="Last Price", value=format_brl(info.last_price))
    cols[3].metric(label="Previous Close", value=format_brl(info.previous_close))
    cols[4].metric(label="Open Price", value=format_brl(info.open_price))
    cols[5].metric(label="Day High", value=format_brl(info.day_high))
    cols[6].metric(label="Day Low", value=format_brl(info.day_low))
