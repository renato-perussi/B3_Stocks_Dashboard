"""Period statistics panel for a single stock."""

from __future__ import annotations

import streamlit as st

from app.models import StockStatistics
from app.ui.formatters import format_brl, format_pct


def render_statistics(stats: StockStatistics) -> None:
    """Render the eight statistics for the selected period in a 2x4 grid."""
    with st.container(border=True, width="stretch", height="content"):
        st.markdown("#### Statistics for the period")

        col_left, col_right = st.columns(2)

        with col_left:
            st.metric(label="Cumulative Return", value=format_pct(stats.cumulative_return))
            st.metric(label="Average Price", value=format_brl(stats.mean_price))
            st.metric(label="Standard Deviation", value=format_brl(stats.standard_deviation))
            st.metric(label="High Price", value=format_brl(stats.high_price))

        with col_right:
            st.metric(label="Annualized Volatility", value=format_pct(stats.volatility))
            st.metric(label="Median Price", value=format_brl(stats.median_price))
            st.metric(label="Coefficient Variation", value=format_pct(stats.coefficient_variation))
            st.metric(label="Low Price", value=format_brl(stats.low_price))
