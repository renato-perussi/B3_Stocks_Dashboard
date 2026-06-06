"""Multi-stock comparison view: selectors, charts and ranking bars."""

from __future__ import annotations

import streamlit as st

from app.analytics import comparison
from app.data.yfinance_client import fetch_close_prices
from app.errors import handle_data_errors
from app.models import ComparisonResult
from app.ui.components.comparison_controls import render_comparison_controls
from app.ui.components.correlation_heatmap import render_correlation_heatmap
from app.ui.components.cumulative_returns_chart import (
    render_cumulative_returns_chart,
)
from app.ui.components.horizontal_bar import render_horizontal_bar


def render_comparison_view() -> None:
    """Render the Statistical Analyses section."""
    st.markdown("## Statistical Analyses")

    selection = render_comparison_controls()
    if len(selection.tickers) < 2:
        st.warning("Please, select at least two stocks for analysis.")
        return

    result = _build_comparison(selection.period, selection.tickers)
    if result is None:
        return

    _render_charts(result)


@handle_data_errors("multi-stock comparison")
def _build_comparison(period: str, tickers: list[str]) -> ComparisonResult | None:
    """Fetch data and compute the comparison analytics."""
    close_prices = fetch_close_prices(period, tickers)
    if close_prices.empty:
        st.warning("No data available for the selected tickers and period.")
        return None

    returns = comparison.calculate_returns(close_prices)
    return ComparisonResult(
        close_prices=close_prices,
        returns=returns,
        cumulative_returns_period=comparison.cumulative_returns_period(returns),
        cumulative_returns_ranking=comparison.cumulative_returns_ranking(returns),
        correlation_matrix=returns.corr(),
        annualized_volatility=comparison.annualized_volatility(returns),
        coefficient_variation=comparison.coefficient_variation(close_prices),
    )


def _render_charts(result: ComparisonResult) -> None:
    """Render the two top charts and the three ranking bars."""
    col_left, col_right = st.columns([0.5, 0.5])
    with col_left:
        render_cumulative_returns_chart(result.cumulative_returns_period)
    with col_right:
        render_correlation_heatmap(result.correlation_matrix)

    bar_col_1, bar_col_2, bar_col_3 = st.columns(3)
    with bar_col_1:
        render_horizontal_bar(
            result.cumulative_returns_ranking,
            title="Cumulative Returns (%)",
            value_column="Cumulative Return",
            x_label="Cumulative Returns (%)",
        )
    with bar_col_2:
        render_horizontal_bar(
            result.annualized_volatility,
            title="Annualized Volatility (%)",
            value_column="Annualized Volatility",
            x_label="Annualized Volatility (%)",
        )
    with bar_col_3:
        render_horizontal_bar(
            result.coefficient_variation,
            title="Coefficient Variation (%)",
            value_column="Coefficient Variation",
            x_label="Coefficient Variation (%)",
        )
