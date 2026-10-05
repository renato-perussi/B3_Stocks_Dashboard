"""Cumulative returns chart."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.constants import CHART_HEIGHT_COMPARISON


def render_cumulative_returns_chart(cumulative_returns: pd.DataFrame) -> None:
    """Show cumulative returns lines."""
    with st.container(border=True, height=CHART_HEIGHT_COMPARISON, width='stretch'):
        st.markdown('### Cumulative Returns (%)')
        st.line_chart(
            data=cumulative_returns,
            height='stretch',
            width='stretch',
            x_label='Dates',
            y_label='Cumulative Returns (%)',
        )
