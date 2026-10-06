"""Tests for yfinance client with mocks."""

import datetime

import pandas as pd


class _FakeTicker:
    """Minimal yfinance stub."""

    def __init__(self, history: pd.DataFrame, info: dict | None = None) -> None:
        """Store fake history and info."""
        self._history = history
        self._info = info or {}
        self.fast_info = {'lastPrice': 10.0}

    def history(self, period: str = '1mo', *args: object, **kwargs: object) -> pd.DataFrame:
        """Return fake history."""
        return self._history

    @property
    def info(self) -> dict:
        """Return fake info dict."""
        return self._info


def test_fetch_history_rounds_and_dates(monkeypatch) -> None:
    """History has Date col and rounded values."""
    import app.data.yfinance_client as client

    idx = pd.DatetimeIndex([pd.Timestamp('2024-01-02'), pd.Timestamp('2024-01-03')])
    fake = pd.DataFrame(
        {
            'Open': [10.1234, 11.5678],
            'High': [10.9, 12.1],
            'Low': [10.0, 11.2],
            'Close': [10.4567, 11.9876],
        },
        index=idx,
    )
    fake.index.name = 'Date'
    monkeypatch.setattr(client.yf, 'Ticker', lambda t, *a, **k: _FakeTicker(fake))
    out = client.fetch_history.__wrapped__('PETR4.SA', '1mo')
    assert 'Date' in out.columns
    assert isinstance(out['Date'].iloc[0], datetime.date)
    assert out['Close'].iloc[0] == round(10.4567, 2)


def test_fetch_close_prices_aligns_tickers(monkeypatch) -> None:
    """Close prices collect per ticker."""
    import app.data.yfinance_client as client

    def _ticker(name: str, *args: object, **kwargs: object) -> _FakeTicker:
        idx = pd.DatetimeIndex([pd.Timestamp('2024-01-02')])
        frame = pd.DataFrame({'High': [42.5], 'Low': [41.5], 'Close': [42.0]}, index=idx)
        return _FakeTicker(frame)

    monkeypatch.setattr(client.yf, 'Ticker', _ticker)
    out = client.fetch_close_prices.__wrapped__('1mo', ['PETR4.SA', 'VALE3.SA'])
    assert set(out.columns) == {'PETR4.SA', 'VALE3.SA'}


def test_fetch_ticker_info_math(monkeypatch) -> None:
    """Ticker info computes pct today."""
    import app.data.yfinance_client as client

    info = {
        'previousClose': 10.0,
        'open': 10.1,
        'dayHigh': 10.5,
        'dayLow': 9.9,
        'longName': 'Test Co',
        'longBusinessSummary': 'Summary.',
        'website': 'https://example.com',
        'sector': 'Energy',
        'industry': 'Oil',
    }
    fake = _FakeTicker(pd.DataFrame(), info=info)
    fake.fast_info = {'lastPrice': 11.0}
    monkeypatch.setattr(client.yf, 'Ticker', lambda t, *a, **k: fake)
    out = client.fetch_ticker_info.__wrapped__('PETR4.SA')
    assert out.ticker == 'PETR4.SA'
    assert out.last_price == 11.0
    assert out.pct_today == (11.0 / 10.0 - 1) * 100
