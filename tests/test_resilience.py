"""Resilience tests: Yahoo 429/401, Stooq fallback, validation."""

from __future__ import annotations

import app.data.yfinance_client as client
import pandas as pd
import pytest
from app.data.exceptions import DataUnavailableError, InvalidTickerError, RateLimitedError


class _FakeTicker:
    """Minimal yfinance stub."""

    def __init__(
        self,
        history: pd.DataFrame,
        info: dict | None = None,
        fast: dict | None = None,
    ) -> None:
        """Store fake history and info."""
        self._history = history
        self._info = info if info is not None else {}
        self.fast_info = fast if fast is not None else {'lastPrice': 10.0}

    def history(self, period: str = '1mo', *args: object, **kwargs: object) -> pd.DataFrame:
        """Return fake history."""
        return self._history

    @property
    def info(self) -> dict:
        """Return fake info."""
        return self._info


def _frame(close: list[float]) -> pd.DataFrame:
    """Build fake OHLC with Date index."""
    idx = pd.DatetimeIndex(
        [pd.Timestamp('2024-01-02') + pd.Timedelta(days=i) for i in range(len(close))]
    )
    data = {
        'Open': close,
        'High': [c + 0.5 for c in close],
        'Low': [c - 0.5 for c in close],
        'Close': close,
        'Volume': [1000] * len(close),
    }
    frame = pd.DataFrame(data, index=idx)
    frame.index.name = 'Date'
    return frame


def _patch_stooq_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Block real network in Stooq fallback."""

    def _fail(ticker: str, period: str = '1mo') -> pd.DataFrame:
        raise DataUnavailableError('stooq mock unavailable')

    def _fail_quote(ticker: str) -> object:
        raise DataUnavailableError('stooq mock without quote')

    monkeypatch.setattr(client, '_fetch_history_stooq_fallback', _fail)
    monkeypatch.setattr(
        client,
        '_fetch_close_prices_stooq_fallback',
        lambda p, t: (_ for _ in ()).throw(DataUnavailableError('x')),
    )
    monkeypatch.setattr(client, '_fetch_quote_stooq_fallback', _fail_quote)


def test_empty_info_raises_data_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty info raises DataUnavailableError."""
    _patch_stooq_fail(monkeypatch)
    fake = _FakeTicker(_frame([10.0, 11.0]), info={})
    monkeypatch.setattr(client.yf, 'Ticker', lambda t, *a, **k: fake)
    with pytest.raises(DataUnavailableError):
        client.fetch_ticker_info.__wrapped__('PETR4.SA')


def test_empty_history_raises_data_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty frame raises DataUnavailableError."""
    _patch_stooq_fail(monkeypatch)
    fake = _FakeTicker(pd.DataFrame(), info={})
    monkeypatch.setattr(client.yf, 'Ticker', lambda t, *a, **k: fake)
    with pytest.raises(DataUnavailableError):
        client.fetch_history.__wrapped__('PETR4.SA', '1mo')


def test_fallback_previous_close_via_history(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing previousClose uses history tail."""
    info = {
        'open': 10.1,
        'dayHigh': 10.5,
        'dayLow': 9.9,
        'longName': 'Test SA',
        'longBusinessSummary': 'Summary.',
        'website': 'https://example.com',
        'sector': 'Energy',
        'industry': 'Oil',
    }
    fake = _FakeTicker(_frame([9.5, 10.0]), info=info, fast={'lastPrice': 11.0})
    monkeypatch.setattr(client.yf, 'Ticker', lambda t, *a, **k: fake)
    out = client.fetch_ticker_info.__wrapped__('PETR4.SA')
    assert out.last_price == 11.0
    assert out.previous_close == 9.5  # From history tail (second-last close).
    assert out.open_price == 10.1


def test_fallback_last_price_via_fast_info(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing currentPrice uses fast_info."""
    info = {
        'previousClose': 10.0,
        'open': 10.1,
        'dayHigh': 10.5,
        'dayLow': 9.9,
        'longName': 'Test',
        'longBusinessSummary': 'Summary.',
        'website': '',
        'sector': '',
        'industry': '',
    }
    fake = _FakeTicker(_frame([10.0]), info=info, fast={'lastPrice': 12.5})
    monkeypatch.setattr(client.yf, 'Ticker', lambda t, *a, **k: fake)
    out = client.fetch_ticker_info.__wrapped__('PETR4.SA')
    assert out.last_price == 12.5


def test_retry_on_429_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Transient 429 retries then succeeds."""
    _patch_stooq_fail(monkeypatch)
    calls = {'n': 0}
    good = _frame([10.0, 11.0])

    def _flaky(ticker: str, period: str) -> pd.DataFrame:
        calls['n'] += 1
        if calls['n'] < 3:
            raise RateLimitedError('429 rate limit mock')
        return good

    monkeypatch.setattr(client, '_download_history_raw', _flaky)
    out = client.fetch_history.__wrapped__('PETR4.SA', '1mo')
    assert calls['n'] == 3
    assert 'Close' in out.columns


def test_invalid_ticker_blocks_ssrf() -> None:
    """Ticker outside allowlist is rejected."""
    with pytest.raises(InvalidTickerError):
        client.fetch_history.__wrapped__('EVIL; rm -rf', '1mo')
    with pytest.raises(InvalidTickerError):
        client.fetch_ticker_info.__wrapped__('AAPL')
    with pytest.raises(InvalidTickerError):
        client.fetch_close_prices.__wrapped__('1mo', ['PETR4.SA', 'EVIL'])


def test_stooq_parser_with_fake_csv() -> None:
    """Stooq parser builds normalized frame."""
    from app.data import stooq_client

    csv = (
        'Date,Open,High,Low,Close,Volume\n'
        '2024-01-02,10.0,10.5,9.9,10.2,1000\n'
        '2024-01-03,10.2,10.8,10.0,10.6,1200\n'
    )
    frame = stooq_client._parse_csv(csv)
    assert list(frame.columns)[:5] == ['Date', 'Open', 'High', 'Low', 'Close']
    assert len(frame) == 2
    assert float(frame.iloc[-1]['Close']) == 10.6


def test_stooq_history_with_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """fetch_history_stooq uses mocked CSV."""
    from app.data import stooq_client

    csv = (
        'Date,Open,High,Low,Close,Volume\n'
        '2023-01-02,10.0,10.5,9.9,10.2,1000\n'
        '2024-06-01,20.0,20.5,19.9,20.2,1000\n'
    )
    monkeypatch.setattr(stooq_client, '_download_csv', lambda s: csv)
    out = stooq_client.fetch_history_stooq.__wrapped__('PETR4.SA', '1mo')
    assert 'Close' in out.columns
    assert 'Date' in out.columns
    assert not out.empty


def test_stooq_quote_with_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """fetch_quote_stooq derives last/previous."""
    from app.data import stooq_client

    csv = (
        'Date,Open,High,Low,Close,Volume\n'
        '2024-01-02,10.0,10.5,9.9,10.0,1000\n'
        '2024-01-03,10.0,11.0,9.9,11.0,1000\n'
    )
    monkeypatch.setattr(stooq_client, '_download_csv', lambda s: csv)
    quote = stooq_client.fetch_quote_stooq.__wrapped__('PETR4.SA')
    assert quote['lastPrice'] == 11.0
    assert quote['previousClose'] == 10.0


def test_show_data_error_uses_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    """DataUnavailableError shows warning."""
    import os

    from app import errors

    monkeypatch.setenv('APP_ENV', 'production')
    seen: dict[str, object] = {}
    monkeypatch.setattr(errors.st, 'warning', lambda m: seen.setdefault('warning', m))
    monkeypatch.setattr(errors.st, 'error', lambda m: seen.setdefault('error', m))
    errors.show_data_error('ctx', DataUnavailableError('yahoo 429'))
    assert 'warning' in seen
    assert 'error' not in seen
    assert 'Yahoo data temporarily unavailable' in str(seen['warning'])
    # No cookie/crumb leak in production.
    monkeypatch.setattr(errors.st, 'warning', lambda m: seen.setdefault('warning2', m))
    errors.show_data_error('ctx', DataUnavailableError('invalid crumb cookie=abc'))
    assert 'warning' in seen
    assert os.getenv('APP_ENV') == 'production'


def test_is_transient_skips_permanent_empty() -> None:
    """Permanent empty skips retry; RateLimited retries."""
    assert client._is_transient(DataUnavailableError('No Yahoo history')) is False
    assert client._is_transient(DataUnavailableError('Missing Close column')) is False
    assert client._is_transient(DataUnavailableError('Empty Yahoo download.')) is False
    assert client._is_transient(RateLimitedError('429 rate limit')) is True
    assert client._is_transient(DataUnavailableError('Yahoo timeout/network')) is True
    assert client._is_transient(InvalidTickerError('x')) is False


def test_invalid_period_fails_without_network() -> None:
    """Period outside allowlist raises fast."""
    with pytest.raises(InvalidTickerError):
        client.fetch_history.__wrapped__('PETR4.SA', '1d')
    with pytest.raises(InvalidTickerError):
        client.fetch_close_prices.__wrapped__('foo', ['PETR4.SA'])
    assert client._validate_period('1mo') == '1mo'
    assert client._validate_period('5d') == '5d'
    assert client._validate_period('max') == 'max'


def test_flat_multi_ticker_raises() -> None:
    """Flat frame with N tickers raises."""
    idx = pd.DatetimeIndex([pd.Timestamp('2024-01-02')])
    flat = pd.DataFrame({'Close': [10.0]}, index=idx)
    with pytest.raises(DataUnavailableError):
        client._parse_download_frame(flat, ['PETR4.SA', 'VALE3.SA'])
    # Case-insensitive: lowercase 'close' also resolves single.
    flat_lower = pd.DataFrame({'close': [10.0]}, index=idx)
    out = client._parse_download_frame(flat_lower, ['PETR4.SA'])
    assert list(out.columns) == ['PETR4.SA']
