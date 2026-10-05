"""Tests for currency and percent formatters."""

from app.ui.formatters import format_brl, format_pct, format_pct_signed


def test_format_brl() -> None:
    """Format BRL with prefix and separators."""
    assert format_brl(1234.5) == 'R$ 1,234.50'
    assert format_brl(0) == 'R$ 0.00'


def test_format_pct() -> None:
    """Format percent with two decimals."""
    assert format_pct(12.3456) == '12.35%'
    assert format_pct(0) == '0.00%'


def test_format_pct_signed() -> None:
    """Format signed percent always with sign."""
    assert format_pct_signed(3.2) == '+3.20%'
    assert format_pct_signed(-3.2) == '-3.20%'
    assert format_pct_signed(0) == '+0.00%'
