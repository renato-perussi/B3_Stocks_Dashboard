"""Tests for error helpers."""

from app import errors


def test_handle_data_errors_success(monkeypatch) -> None:
    """Passthrough on success."""

    @errors.handle_data_errors('ctx')
    def _ok() -> int:
        """Return one."""
        return 1

    assert _ok() == 1


def test_handle_data_errors_returns_none(monkeypatch) -> None:
    """Return None and show UI on failure."""
    calls: list[str] = []
    monkeypatch.setattr(errors, 'show_data_error', lambda c, e: calls.append(c))

    @errors.handle_data_errors('my ctx')
    def _boom() -> int:
        """Always fail."""
        raise ValueError('boom')

    assert _boom() is None
    assert calls == ['my ctx']


def test_show_data_error_renders(monkeypatch) -> None:
    """Error helper calls streamlit."""
    import contextlib

    seen: dict[str, object] = {}
    monkeypatch.setattr(errors.st, 'error', lambda m: seen.setdefault('error', m))
    monkeypatch.setattr(errors.st, 'exception', lambda e: seen.setdefault('exc', e))

    @contextlib.contextmanager
    def _expander(label: str):
        """Fake expander."""
        yield None

    monkeypatch.setattr(errors.st, 'expander', _expander)
    errors.show_data_error('ctx', ValueError('x'))
    assert 'error' in seen
    assert 'exc' in seen
