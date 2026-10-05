"""Display formatters."""

from __future__ import annotations

from app.constants import CURRENCY_PREFIX


def format_brl(value: float) -> str:
    """Format BRL with separator."""
    return f'{CURRENCY_PREFIX}{value:,.2f}'


def format_pct(value: float) -> str:
    """Format percent with decimals."""
    return f'{value:,.2f}%'


def format_pct_signed(value: float) -> str:
    """Format signed percent."""
    return f'{value:+,.2f}%'
