"""Generic horizontal bar chart used for ranking views."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.constants import CHART_HEIGHT_COMPARISON


def render_horizontal_bar(
    data: pd.DataFrame,
    *,
    title: str,
    value_column: str,
    x_label: str,
) -> None:
    """Render a horizontal bar chart sorted by ``value_column``."""
    with st.container(border=True, height=CHART_HEIGHT_COMPARISON, width="stretch"):
        st.markdown(f"### {title}")
        st.bar_chart(
            data=data,
            x="Ticker",
            y=value_column,
            horizontal=True,
            sort=False,
            y_label="Tickers",
            x_label=x_label,
            height="stretch",
            width="stretch",
        )
