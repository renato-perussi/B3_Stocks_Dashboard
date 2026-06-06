"""Display formatters for currency and percentages."""

from __future__ import annotations

from app.constants import CURRENCY_PREFIX


def format_brl(value: float) -> str:
    """Format a value as Brazilian Real with thousands separator."""
    return f"{CURRENCY_PREFIX}{value:,.2f}"


def format_pct(value: float) -> str:
    """Format a value as a percentage with two decimals."""
    return f"{value:,.2f}%"


def format_pct_signed(value: float) -> str:
    """Format a percentage always with sign and two decimals."""
    return f"{value:+,.2f}%"
