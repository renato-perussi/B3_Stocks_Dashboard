"""About popover for ticker."""

from __future__ import annotations

import streamlit as st

from app.models import TickerInfo


def render_about(info: TickerInfo) -> None:
    """Show company profile popover."""
    with st.popover('About', use_container_width=True):
        st.markdown(f'## {info.long_name}')
        for paragraph in info.summary.split('. '):
            st.write(paragraph.strip() + '.')
        st.write(f'**Website:** {info.web_site}')
        st.write(f'**Sector:** {info.sector} | **Industry:** {info.industry}')
