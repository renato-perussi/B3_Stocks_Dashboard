"""Stooq fallback client."""

from __future__ import annotations

import io
import logging
from datetime import date

import pandas as pd
import requests
import streamlit as st

from app.config import STOCKS
from app.constants import CACHE_TTL_HISTORY
from app.data.exceptions import DataUnavailableError, InvalidTickerError

logger = logging.getLogger(__name__)

_STOOQ_URL = 'https://stooq.com/q/d/l/'
_TIMEOUT = 15
_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
)

# Map app periods to Stooq day windows.
_PERIOD_DAYS: dict[str, int | None] = {
    '1mo': 31,
    '3mo': 93,
    '6mo': 186,
    '1y': 365,
    '2y': 730,
    '5y': 1825,
    '10y': 3650,
    'ytd': None,
    '5d': 7,
    'max': None,
}


def _validate_ticker(ticker: str) -> str:
    """Validate against allowlist."""
    upper = (ticker or '').strip().upper()
    if upper not in STOCKS:
        raise InvalidTickerError(f'Invalid ticker: {ticker!r}.')
    return upper.lower()


def _download_csv(stooq_symbol: str) -> str:
    """Download Stooq daily CSV."""
    try:
        resp = requests.get(
            _STOOQ_URL,
            params={'s': stooq_symbol, 'f': 'sd2t2ohlcv', 'h': '', 'e': 'csv'},
            headers={'User-Agent': _USER_AGENT},
            timeout=_TIMEOUT,
        )
    except (requests.Timeout, requests.ConnectionError) as exc:
        raise DataUnavailableError(
            f'Stooq unavailable for {stooq_symbol}: timeout/network.'
        ) from exc
    except requests.RequestException as exc:
        raise DataUnavailableError(f'Stooq unavailable for {stooq_symbol}.') from exc
    if resp.status_code == 429:
        raise DataUnavailableError('Stooq rate-limited (429).')
    if resp.status_code != 200 or not resp.text.strip():
        raise DataUnavailableError(f'No Stooq data for {stooq_symbol}.')
    # Stooq returns header + 'No data' for expired symbols.
    first_lines = resp.text.strip().splitlines()
    if len(first_lines) <= 1 or 'No data' in resp.text:
        raise DataUnavailableError(f'No Stooq data for {stooq_symbol}.')
    return resp.text


def _parse_csv(text: str) -> pd.DataFrame:
    """Parse Stooq CSV into normalized frame."""
    frame = pd.read_csv(io.StringIO(text))
    # Normalize columns: Date, Open, High, Low, Close, Volume.
    cols = {c.lower(): c for c in frame.columns}
    if 'date' not in cols or 'close' not in cols:
        raise DataUnavailableError('Stooq CSV missing Date/Close columns.')
    frame = frame.rename(columns={v: k.capitalize() for k, v in cols.items()})
    frame['Date'] = pd.to_datetime(frame['Date'], errors='coerce')
    frame = frame.dropna(subset=['Date', 'Close'])
    if frame.empty:
        raise DataUnavailableError('Empty Stooq CSV after parsing.')
    frame = frame.sort_values('Date').round(2)
    return frame


def _apply_period(frame: pd.DataFrame, period: str) -> pd.DataFrame:
    """Filter frame by app period."""
    if period == 'max':
        return frame.reset_index(drop=True)
    if period == 'ytd':
        start = date(date.today().year, 1, 1)
        frame = frame[frame['Date'] >= pd.Timestamp(start)]
        return frame.reset_index(drop=True)
    days = _PERIOD_DAYS.get(period, 365)
    if days is not None:
        cutoff = frame['Date'].max() - pd.Timedelta(days=days)
        frame = frame[frame['Date'] >= cutoff]
    return frame.reset_index(drop=True)


@st.cache_data(ttl=CACHE_TTL_HISTORY, show_spinner=False)
def fetch_history_stooq(ticker: str, period: str) -> pd.DataFrame:
    """Stooq OHLC history with Date/Close columns."""
    symbol = _validate_ticker(ticker)
    logger.info('Using Stooq fallback for %s (%s).', ticker, period)
    text = _download_csv(symbol)
    frame = _parse_csv(text)
    frame = _apply_period(frame, period)
    if frame.empty or 'Close' not in frame.columns:
        raise DataUnavailableError(f'No Stooq data for {ticker} in period {period}.')
    out = frame.copy()
    out['Date'] = pd.to_datetime(out['Date']).dt.date
    return out.round(2)


@st.cache_data(ttl=CACHE_TTL_HISTORY, show_spinner=False)
def fetch_quote_stooq(ticker: str) -> dict[str, float | str]:
    """Current/previous Stooq quote."""
    symbol = _validate_ticker(ticker)
    text = _download_csv(symbol)
    frame = _parse_csv(text)
    if frame.empty or len(frame) < 1:
        raise DataUnavailableError(f'No Stooq quote for {ticker}.')
    last_row = frame.iloc[-1]
    prev_row = frame.iloc[-2] if len(frame) >= 2 else last_row
    last = float(last_row['Close'])
    previous = float(prev_row['Close'])
    open_price = float(last_row.get('Open', last)) if 'Open' in frame.columns else last
    high = float(last_row.get('High', last)) if 'High' in frame.columns else last
    low = float(last_row.get('Low', last)) if 'Low' in frame.columns else last
    return {
        'lastPrice': round(last, 2),
        'previousClose': round(previous, 2),
        'open': round(open_price, 2),
        'dayHigh': round(high, 2),
        'dayLow': round(low, 2),
        'longName': ticker,
        'longBusinessSummary': '',
        'website': '',
        'sector': '',
        'industry': '',
    }
