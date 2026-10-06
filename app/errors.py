"""Error helpers for UI."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

import streamlit as st

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

_FRIENDLY_UNAVAILABLE = (
    'Yahoo data temporarily unavailable (cloud rate limit). Trying fallback source automatically.'
)

_SENSITIVE_MARKERS = ('cookie', 'crumb', 'set-cookie', 'authorization')


def _is_dev() -> bool:
    """Check dev environment flag."""
    env = os.getenv('APP_ENV', os.getenv('ENVIRONMENT', 'production')).lower()
    return env in ('dev', 'development', 'local', 'test', 'testing')


def _sanitize(message: str) -> str:
    """Strip sensitive cookie/crumb markers."""
    lowered = message.lower()
    if any(marker in lowered for marker in _SENSITIVE_MARKERS):
        return 'Technical detail hidden for security (provider auth).'
    if len(message) > 500:
        return message[:500] + '…'
    return message


def _is_unavailable(exc: Exception) -> bool:
    """Classify transient data errors."""
    name = type(exc).__name__
    if name in ('DataUnavailableError', 'RateLimitedError'):
        return True
    # Fallback by qualified name (avoids circular app.data import).
    module = getattr(type(exc), '__module__', '') or ''
    if 'DataUnavailable' in name or 'RateLimited' in name:
        return True
    return ('data.exceptions' in module and 'Unavailable' in name) or 'RateLimited' in name


def show_data_error(context: str, exc: Exception) -> None:
    """Log and show friendly error."""
    if _is_unavailable(exc):
        logger.warning('Data unavailable in %s: %s', context, _sanitize(str(exc)))
        st.warning(_FRIENDLY_UNAVAILABLE)
        if _is_dev():
            with st.expander('Error details'):
                st.exception(exc)
        return
    logger.warning('Data error in %s: %s', context, _sanitize(str(exc)))
    st.error(f'Could not load data for {context}. Please check connection and retry.')
    if _is_dev():
        with st.expander('Error details'):
            st.exception(exc)


def handle_data_errors(context: str) -> Callable[[F], F]:
    """Decorate loaders with friendly error UI."""

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                show_data_error(context, exc)
                return None

        return cast(F, wrapper)

    return decorator
