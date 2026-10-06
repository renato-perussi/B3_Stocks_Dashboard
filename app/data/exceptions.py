"""Domain exceptions for data layer."""

from __future__ import annotations


class DataUnavailableError(Exception):
    """Transient data fetch failure."""


class RateLimitedError(DataUnavailableError):
    """Yahoo rate limit (HTTP 429/401)."""


class InvalidTickerError(Exception):
    """Ticker outside allowed universe."""
