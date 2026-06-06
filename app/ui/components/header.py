"""Header with B3 logo."""

from __future__ import annotations

import streamlit as st

from app.constants import LOGO_PATH


def render_header() -> None:
    """Render the B3 logo on the left column header."""
    with st.container(
        width="stretch",
        vertical_alignment="center",
        horizontal_alignment="left",
    ):
        st.image(image=LOGO_PATH, width=170)
