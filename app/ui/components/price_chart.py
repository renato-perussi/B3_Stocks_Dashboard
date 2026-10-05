"""Close price chart."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.constants import CHART_HEIGHT_SINGLE


def render_price_chart(history: pd.DataFrame) -> None:
    """Show close price lines."""
    with st.container(border=True, height=CHART_HEIGHT_SINGLE, width='stretch'):
        st.line_chart(
            data=history,
            x='Date',
            y='Close',
            height='stretch',
            width='stretch',
            x_label='Dates',
            y_label='Close Prices (R$)',
        )
