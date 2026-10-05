"""Correlation heatmap view."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from seaborn import heatmap

from app.constants import CHART_HEIGHT_COMPARISON


def render_correlation_heatmap(correlation_matrix: pd.DataFrame) -> None:
    """Show pairwise correlation heatmap."""
    with st.container(border=True, height=CHART_HEIGHT_COMPARISON, width='stretch'):
        st.markdown('### Correlation Heatmap')
        figure = plt.figure(figsize=(12, 6.5))
        heatmap(correlation_matrix, annot=True, cmap='Blues', vmin=-1, vmax=1)
        st.pyplot(figure, width='stretch')
        plt.close(figure)
