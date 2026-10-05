"""Error helpers for UI."""

from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

import streamlit as st

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def show_data_error(context: str, exc: Exception) -> None:
    """Log and show friendly load error."""
    logger.exception('Data error in %s', context)
    st.error(f'Could not load data for {context}. Please check connection and retry.')
    with st.expander('Error details'):
        st.exception(exc)


def handle_data_errors(context: str) -> Callable[[F], F]:
    """Wrap loader with friendly error UI."""

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
