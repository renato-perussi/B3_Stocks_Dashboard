"""Application entry point.

Run from the project root with: streamlit run app/main.py

The ``sys.path`` bootstrap at the top of this module ensures the project
root is on the import path regardless of how Streamlit is invoked, so
``from app import ...`` resolves correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st  # noqa: E402

from app.constants import PAGE_TITLE  # noqa: E402
from app.ui.components.header import render_header  # noqa: E402
from app.ui.views.comparison_view import render_comparison_view  # noqa: E402
from app.ui.views.single_stock_view import render_single_stock_view  # noqa: E402


def main() -> None:
    """Render the full dashboard organized in two tabs."""
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")

    render_header()

    tab_single, tab_compare = st.tabs(["Single Stock", "Multiple Stocks"])
    with tab_single:
        render_single_stock_view()
    with tab_compare:
        render_comparison_view()


if __name__ == "__main__":
    main()
