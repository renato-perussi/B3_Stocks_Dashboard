"""Resilient Yahoo Finance client with retry and Stooq fallback."""

from __future__ import annotations

import logging
import random
import time
from contextlib import suppress
from typing import Any

import pandas as pd
import streamlit as st
import yfinance as yf

from app.config import PERIODS, STOCKS
from app.constants import CACHE_TTL_HISTORY, CACHE_TTL_INFO
from app.data.exceptions import DataUnavailableError, InvalidTickerError, RateLimitedError
from app.models import TickerInfo

logger = logging.getLogger(__name__)

_BROWSER_UA = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
)

# Explicit Yahoo timeout (15s, same as Stooq).
# Tenacity retry (3 attempts with backoff) bounds total time.
_YAHOO_TIMEOUT = 15

# Periods accepted without network: UI (PERIODS) + '5d' + 'max'.
_VALID_PERIODS = frozenset([*PERIODS, '5d', 'max'])

try:  # Optional tenacity: exponential backoff retry.
    from tenacity import (
        retry,
        retry_if_exception,
        stop_after_attempt,
        wait_exponential_jitter,
    )

    _HAS_TENACITY = True
except ImportError:  # pragma: no cover - manual fallback.
    _HAS_TENACITY = False


def _is_transient(exc: BaseException) -> bool:
    """Retry transient errors only."""
    if isinstance(exc, InvalidTickerError):
        return False
    if isinstance(exc, RateLimitedError):
        return True
    _transient_markers = (
        '429',
        '401',
        'rate limit',
        'rate-limit',
        'ratelimit',
        'invalid crumb',
        'crumb',
        'unauthorized',
        'too many requests',
        'timeout',
        'timed out',
        'connection',
        'http error',
    )
    if isinstance(exc, DataUnavailableError):
        msg = str(exc).lower()
        return any(m in msg for m in _transient_markers)
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True
    msg = str(exc).lower()
    return any(m in msg for m in _transient_markers)


def _classify_yahoo_error(exc: Exception, context: str) -> DataUnavailableError:
    """Map raw Yahoo error to domain exception."""
    msg = str(exc).lower()
    if any(
        m in msg for m in ('429', '401', 'invalid crumb', 'crumb', 'rate limit', 'unauthorized')
    ):
        return RateLimitedError(f'Yahoo rate-limited in {context} (try later).')
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return DataUnavailableError(f'Yahoo timeout/network in {context}.')
    return DataUnavailableError(f'Yahoo unavailable in {context}.')


def _validate_ticker(ticker: str) -> str:
    """Validate ticker against allowlist."""
    upper = (ticker or '').strip().upper()
    if upper not in STOCKS:
        raise InvalidTickerError(f'Invalid ticker: {ticker!r}.')
    return upper


def _validate_period(period: str) -> str:
    """Validate period without network."""
    cleaned = (period or '').strip()
    if cleaned not in _VALID_PERIODS:
        raise InvalidTickerError(f'Invalid period: {period!r}.')
    return cleaned


def _build_session() -> Any | None:
    """Build curl-cffi session with browser fingerprint."""
    try:
        from curl_cffi import requests as cffi_requests

        session: Any = cffi_requests.Session(impersonate='chrome')
        with suppress(Exception):
            session.headers.update({'User-Agent': _BROWSER_UA})
        return session
    except ImportError:
        logger.debug('curl-cffi unavailable; using default yfinance session.')
        return None
    except Exception as exc:
        logger.debug('Failed to build curl-cffi session: %s', type(exc).__name__)
        return None


def _get_ticker(ticker: str) -> Any:
    """Build yf.Ticker with browser-like session."""
    session = _build_session()
    try:
        if session is not None:
            return yf.Ticker(ticker, session=session)
        return yf.Ticker(ticker)
    except TypeError:
        # Compat with test stubs and old yfinance.
        return yf.Ticker(ticker)


def _safe_info_get(info: Any, key: str) -> Any | None:
    """Read dict-like info key safely."""
    if info is None:
        return None
    try:
        if isinstance(info, dict):
            return info.get(key)
        get = getattr(info, 'get', None)
        if callable(get):
            return get(key)
        return info[key]
    except Exception:
        return None


def _safe_fast_get(fast_info: Any, key: str) -> Any | None:
    """Read fast_info safely."""
    if fast_info is None:
        return None
    try:
        if isinstance(fast_info, dict):
            return fast_info.get(key)
        try:
            return fast_info[key]
        except Exception:
            pass
        get = getattr(fast_info, 'get', None)
        if callable(get):
            try:
                return get(key)
            except Exception:
                return None
        return getattr(fast_info, key, None)
    except Exception:
        return None


def _to_float(value: Any) -> float | None:
    """Parse float or None."""
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    # NaN/inf are invalid quotes.
    if result != result or result in (float('inf'), float('-inf')):
        return None
    return result


def _first_valid(*candidates: Any) -> float | None:
    """Return first float-parseable candidate."""
    for candidate in candidates:
        parsed = _to_float(candidate)
        if parsed is not None:
            return parsed
    return None


def _round2(value: float | None) -> float:
    """Round value (caller ensures non-None)."""
    assert value is not None
    return round(float(value), 2)


def _retry_manual(func: Any, *args: Any, **kwargs: Any) -> Any:
    """Manual retry without tenacity."""
    last: Exception | None = None
    for attempt in range(3):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            if not _is_transient(exc):
                raise
            last = exc
            if attempt < 2:
                delay = (2**attempt) + random.uniform(0, 1)
                logger.debug(
                    'Manual retry %s attempt %d in %.1fs.', func.__name__, attempt + 1, delay
                )
                time.sleep(delay)
    assert last is not None
    raise last


def _with_retry(func: Any) -> Any:
    """Wrap Yahoo call with tenacity retry."""
    if not _HAS_TENACITY:
        return func
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=8, jitter=1),
        retry=retry_if_exception(_is_transient),
        reraise=True,
    )(func)


def _download_history_raw(ticker: str, period: str) -> pd.DataFrame:
    """Raw yfinance download without cache."""
    validated = _validate_ticker(ticker)
    validated_period = _validate_period(period)
    stock = _get_ticker(validated)
    try:
        try:
            frame = stock.history(period=validated_period, timeout=_YAHOO_TIMEOUT)
        except TypeError:
            # Compat with test stubs and old yfinance.
            frame = stock.history(period=validated_period)
    except Exception as exc:
        raise _classify_yahoo_error(exc, f'history {validated}') from None
    return frame


def _normalize_history(frame: pd.DataFrame, ticker: str, period: str) -> pd.DataFrame:
    """Validate and normalize OHLC frame."""
    if frame is None or not isinstance(frame, pd.DataFrame) or frame.empty:
        raise DataUnavailableError(f'No Yahoo history for {ticker} ({period}).')
    cols = list(frame.columns)
    close_col: str | None = None
    for col in cols:
        if str(col).lower() == 'close':
            close_col = str(col)
            break
    if close_col is None:
        # Old yfinance may expose only 'Adj Close'.
        for col in cols:
            if str(col).lower() in ('adj close', 'adj_close'):
                close_col = str(col)
                break
    if close_col is None or frame[close_col].dropna().empty:
        raise DataUnavailableError(f'Missing Close column for {ticker} ({period}).')
    if close_col != 'Close':
        frame = frame.rename(columns={close_col: 'Close'})
    # High/Low required for statistics.
    lower_map = {str(c).lower(): str(c) for c in frame.columns}
    high_col = lower_map.get('high')
    low_col = lower_map.get('low')
    if high_col is None or low_col is None:
        raise DataUnavailableError(f'Missing High/Low columns for {ticker} ({period}).')
    rename: dict[str, str] = {}
    if high_col != 'High':
        rename[high_col] = 'High'
    if low_col != 'Low':
        rename[low_col] = 'Low'
    if rename:
        frame = frame.rename(columns=rename)
    out = frame.copy()
    # 'Date' may come as index or column.
    if 'Date' not in out.columns:
        idx_name = getattr(out.index, 'name', None)
        if isinstance(out.index, pd.DatetimeIndex) or idx_name in ('Date', 'Datetime'):
            out = out.reset_index()
            first = out.columns[0]
            if 'Date' not in out.columns and 'Datetime' in out.columns:
                out = out.rename(columns={'Datetime': 'Date'})
            elif 'Date' not in out.columns:
                out = out.rename(columns={first: 'Date'})
        else:
            raise DataUnavailableError(f'Missing Date column for {ticker} ({period}).')
    out['Date'] = pd.to_datetime(out['Date'], utc=True, errors='coerce')
    out = out.dropna(subset=['Date', 'Close'])
    if out.empty:
        raise DataUnavailableError(f'Empty history after cleaning for {ticker} ({period}).')
    out = out.reset_index(drop=True).round(2)
    # Convert to date for UI/stats.
    out['Date'] = out['Date'].dt.date
    return out


def _fetch_history_yahoo(ticker: str, period: str) -> pd.DataFrame:
    """Yahoo-only history with retry."""
    validated = _validate_ticker(ticker)
    validated_period = _validate_period(period)

    def _do() -> pd.DataFrame:
        raw = _download_history_raw(validated, validated_period)
        return _normalize_history(raw, validated, validated_period)

    if _HAS_TENACITY:
        return _with_retry(_do)()
    return _retry_manual(_do)


def _fetch_ticker_info_yahoo(ticker: str) -> TickerInfo:
    """Yahoo-only quote with retry."""
    validated = _validate_ticker(ticker)

    def _do() -> TickerInfo:
        stock = _get_ticker(validated)
        try:
            info: Any = stock.info
            if callable(info):
                info = info()
        except Exception as exc:
            raise _classify_yahoo_error(exc, f'info {validated}') from None
        if not info:
            raise DataUnavailableError(f'Empty Yahoo info for {validated}.')
        try:
            fast = stock.fast_info
        except Exception:
            fast = None
        # Ordered fallback: info -> fast_info -> history.
        hist_close_last: float | None = None
        hist_close_prev: float | None = None
        try:
            try:
                raw_hist = stock.history(period='5d', timeout=_YAHOO_TIMEOUT)
            except TypeError:
                # Compat with test stubs and old yfinance.
                raw_hist = stock.history(period='5d')
            if isinstance(raw_hist, pd.DataFrame) and not raw_hist.empty:
                close_series = None
                for col in raw_hist.columns:
                    if str(col).lower() == 'close':
                        close_series = raw_hist[col].dropna()
                        break
                if close_series is not None and len(close_series) >= 1:
                    hist_close_last = _to_float(close_series.iloc[-1])
                    hist_close_prev = (
                        _to_float(close_series.iloc[-2]) if len(close_series) >= 2 else None
                    )
        except Exception:
            pass
        last = _first_valid(
            _safe_info_get(info, 'currentPrice'),
            _safe_info_get(info, 'regularMarketPrice'),
            _safe_fast_get(fast, 'lastPrice'),
            _safe_fast_get(fast, 'last_price'),
            hist_close_last,
        )
        previous = _first_valid(
            _safe_info_get(info, 'previousClose'),
            _safe_info_get(info, 'regularMarketPreviousClose'),
            _safe_fast_get(fast, 'previousClose'),
            hist_close_prev,
        )
        open_price = _first_valid(
            _safe_info_get(info, 'open'),
            _safe_info_get(info, 'regularMarketOpen'),
            _safe_fast_get(fast, 'open'),
            hist_close_last,
        )
        high = _first_valid(
            _safe_info_get(info, 'dayHigh'),
            _safe_info_get(info, 'regularMarketDayHigh'),
            _safe_fast_get(fast, 'dayHigh'),
            hist_close_last,
        )
        low = _first_valid(
            _safe_info_get(info, 'dayLow'),
            _safe_info_get(info, 'regularMarketDayLow'),
            _safe_fast_get(fast, 'dayLow'),
            hist_close_last,
        )
        if last is None or previous is None:
            raise DataUnavailableError(f'No Yahoo quote for {validated} (crumb/rate-limit?).')
        pct_today = 0.0 if previous == 0 else (last / previous - 1) * 100
        long_name = str(
            _safe_info_get(info, 'longName') or _safe_info_get(info, 'shortName') or validated
        )
        summary = str(_safe_info_get(info, 'longBusinessSummary') or '')
        website = str(_safe_info_get(info, 'website') or '')
        sector = str(_safe_info_get(info, 'sector') or '')
        industry = str(_safe_info_get(info, 'industry') or '')
        return TickerInfo(
            ticker=validated,
            last_price=_round2(last),
            previous_close=_round2(previous),
            pct_today=float(pct_today),
            open_price=_round2(open_price if open_price is not None else last),
            day_high=_round2(high if high is not None else last),
            day_low=_round2(low if low is not None else last),
            long_name=long_name,
            summary=summary,
            web_site=website,
            sector=sector,
            industry=industry,
        )

    if _HAS_TENACITY:
        return _with_retry(_do)()
    return _retry_manual(_do)


def _parse_download_frame(data: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    """Extract Close matrix from yf.download."""
    if data is None or data.empty:
        raise DataUnavailableError('Empty Yahoo download.')
    closes = pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        level0 = [str(c) for c in data.columns.get_level_values(0).unique()]
        # group_by='ticker': level 0 is ticker.
        if any(t in level0 for t in tickers):
            for ticker in tickers:
                if ticker in data.columns.get_level_values(0):
                    sub = data[ticker]
                    col = None
                    for cand in ('Close', 'close', 'Adj Close'):
                        if cand in sub.columns:
                            col = cand
                            break
                    if col is not None:
                        closes[ticker] = sub[col]
        else:  # group_by='column' fallback: level 0 is OHLC.
            if 'Close' in level0:
                sub = data['Close']
                for ticker in tickers:
                    if ticker in sub.columns:
                        closes[ticker] = sub[ticker]
    else:
        # Flat columns: case-insensitive search.
        close_col: str | None = next(
            (str(c) for c in data.columns if str(c).lower() == 'close'), None
        )
        if close_col is None:
            close_col = next(
                (str(c) for c in data.columns if str(c).lower() in ('adj close', 'adj_close')),
                None,
            )
        if close_col is None:
            raise DataUnavailableError('Yahoo download without usable Close.')
        if len(tickers) == 1:
            # Single ticker returns flat columns.
            closes[tickers[0]] = data[close_col]
        else:
            # Unexpected flat response for multiple tickers.
            raise DataUnavailableError('Unexpected flat response for multiple tickers.')
    # Normalize datetime index.
    with suppress(Exception):
        closes.index = pd.to_datetime(closes.index, utc=True)
    closes = closes.dropna(how='all')
    if closes.empty or closes.shape[1] == 0:
        raise DataUnavailableError('Yahoo download without usable Close.')
    return closes


def _download_batch_raw(period: str, tickers: list[str]) -> pd.DataFrame:
    """Batch download via yf.download."""
    validated_period = _validate_period(period)
    session = _build_session()
    base_kwargs: dict[str, Any] = {
        'period': validated_period,
        'group_by': 'ticker',
        'auto_adjust': True,
        'progress': False,
        'timeout': _YAHOO_TIMEOUT,
    }
    try:
        if session is not None:
            try:
                data = yf.download(list(tickers), session=session, **base_kwargs)
            except TypeError as exc:
                # Old yfinance or stub without session/timeout.
                if 'timeout' in str(exc).lower() or 'session' in str(exc).lower():
                    fallback_kwargs = {k: v for k, v in base_kwargs.items() if k != 'timeout'}
                    try:
                        data = yf.download(list(tickers), session=session, **fallback_kwargs)
                    except TypeError:
                        data = yf.download(list(tickers), **fallback_kwargs)
                else:
                    data = yf.download(list(tickers), **base_kwargs)
        else:
            try:
                data = yf.download(list(tickers), **base_kwargs)
            except TypeError:
                fallback_kwargs = {k: v for k, v in base_kwargs.items() if k != 'timeout'}
                data = yf.download(list(tickers), **fallback_kwargs)
    except Exception as exc:
        raise _classify_yahoo_error(exc, f'batch {validated_period}') from None
    return _parse_download_frame(data, list(tickers))


def _fetch_close_prices_yahoo(period: str, tickers: list[str]) -> pd.DataFrame:
    """Yahoo-only closes with batch/loop fallback."""
    validated_period = _validate_period(period)
    validated = [_validate_ticker(t) for t in tickers]

    def _do_batch() -> pd.DataFrame:
        try:
            return _download_batch_raw(validated_period, validated)
        except DataUnavailableError:
            # Loop fallback tolerating one bad ticker.
            closes = pd.DataFrame()
            failures = 0
            for ticker in validated:
                try:
                    raw = _download_history_raw(ticker, validated_period)
                    norm = _normalize_history(raw, ticker, validated_period)
                    # Align by Date for comparison.
                    series = pd.Series(
                        norm['Close'].to_numpy(),
                        index=pd.to_datetime(pd.Series(norm['Date']), utc=True),
                        name=ticker,
                    )
                    closes[ticker] = series
                except DataUnavailableError:
                    failures += 1
                    continue
            closes = closes.dropna(how='all')
            if closes.empty or closes.shape[1] == 0:
                raise DataUnavailableError(f'No Yahoo closes for {validated_period}.') from None
            return closes

    if _HAS_TENACITY:
        return _with_retry(_do_batch)()
    return _retry_manual(_do_batch)


def _fetch_history_stooq_fallback(ticker: str, period: str) -> pd.DataFrame:
    """Stooq fallback with late import."""
    from app.data import stooq_client

    return stooq_client.fetch_history_stooq(ticker, period)


def _fetch_close_prices_stooq_fallback(period: str, tickers: list[str]) -> pd.DataFrame:
    """Build Close matrix via Stooq."""
    from concurrent.futures import ThreadPoolExecutor

    from app.data import stooq_client

    validated_period = _validate_period(period)

    def _fetch_one(ticker: str) -> tuple[str, pd.DataFrame | None]:
        last_exc: Exception | None = None
        for attempt in range(2):
            try:
                frame = stooq_client.fetch_history_stooq(ticker, validated_period)
                return ticker, frame
            except InvalidTickerError:
                raise
            except Exception as exc:
                last_exc = exc
                if attempt < 1:
                    time.sleep(random.uniform(0.2, 0.6) * (attempt + 1))
        logger.debug('Stooq failed for %s after retry: %s', ticker, type(last_exc).__name__)
        return ticker, None

    ordered: dict[str, pd.Series] = {}
    failures = 0
    max_workers = min(4, max(1, len(tickers)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # map preserves input order.
        for ticker, frame in executor.map(_fetch_one, list(tickers)):
            if frame is None or frame.empty or 'Close' not in frame.columns:
                failures += 1
                continue
            ordered[ticker] = pd.Series(
                frame['Close'].to_numpy(),
                index=pd.to_datetime(pd.Series(frame['Date']), utc=True),
                name=ticker,
            )
    closes = pd.DataFrame()
    for ticker in tickers:
        if ticker in ordered:
            closes[ticker] = ordered[ticker]
    closes = closes.dropna(how='all')
    if closes.empty:
        raise DataUnavailableError(f'No Stooq closes for {validated_period}.')
    return closes


def _fetch_quote_stooq_fallback(ticker: str) -> TickerInfo:
    """Build TickerInfo from Stooq quote."""
    from app.data import stooq_client

    quote = stooq_client.fetch_quote_stooq(ticker)
    last = _to_float(quote.get('lastPrice'))
    previous = _to_float(quote.get('previousClose'))
    if last is None or previous is None:
        raise DataUnavailableError(f'No Stooq quote for {ticker}.')
    pct = 0.0 if previous == 0 else (last / previous - 1) * 100
    validated = _validate_ticker(ticker)
    return TickerInfo(
        ticker=validated,
        last_price=_round2(last),
        previous_close=_round2(previous),
        pct_today=float(pct),
        open_price=_round2(_to_float(quote.get('open')) or last),
        day_high=_round2(_to_float(quote.get('dayHigh')) or last),
        day_low=_round2(_to_float(quote.get('dayLow')) or last),
        long_name=str(quote.get('longName') or validated),
        summary=str(quote.get('longBusinessSummary') or ''),
        web_site=str(quote.get('website') or ''),
        sector=str(quote.get('sector') or ''),
        industry=str(quote.get('industry') or ''),
    )


@st.cache_data(ttl=CACHE_TTL_HISTORY, show_spinner=False)
def fetch_history(ticker: str, period: str) -> pd.DataFrame:
    """Load OHLC history (Yahoo primary, Stooq fallback)."""
    validated = _validate_ticker(ticker)
    validated_period = _validate_period(period)
    try:
        return _fetch_history_yahoo(validated, validated_period)
    except InvalidTickerError:
        raise
    except (DataUnavailableError, RateLimitedError) as yahoo_exc:
        logger.warning('Yahoo failed (%s); trying Stooq.', type(yahoo_exc).__name__)
        try:
            out = _fetch_history_stooq_fallback(validated, validated_period)
        except (DataUnavailableError, InvalidTickerError) as stooq_exc:
            raise DataUnavailableError(
                f'Data unavailable for {validated} on Yahoo and Stooq.'
            ) from stooq_exc
        logger.info('Source used for %s (%s): stooq.', validated, validated_period)
        return out


@st.cache_data(ttl=CACHE_TTL_HISTORY, show_spinner=False)
def fetch_close_prices(period: str, tickers: list[str]) -> pd.DataFrame:
    """Load close series (Yahoo batch, Stooq fallback)."""
    validated_period = _validate_period(period)
    validated = [_validate_ticker(t) for t in tickers]
    try:
        return _fetch_close_prices_yahoo(validated_period, validated)
    except InvalidTickerError:
        raise
    except (DataUnavailableError, RateLimitedError) as yahoo_exc:
        logger.warning('Yahoo batch failed (%s); trying Stooq.', type(yahoo_exc).__name__)
        try:
            out = _fetch_close_prices_stooq_fallback(validated_period, validated)
        except (DataUnavailableError, InvalidTickerError) as stooq_exc:
            raise DataUnavailableError('Data unavailable on Yahoo and Stooq.') from stooq_exc
        logger.info('Source used for batch (%s): stooq.', validated_period)
        return out


@st.cache_data(ttl=CACHE_TTL_INFO, show_spinner=False)
def fetch_ticker_info(ticker: str) -> TickerInfo:
    """Load quote and profile (Yahoo primary, Stooq fallback)."""
    validated = _validate_ticker(ticker)
    try:
        info = _fetch_ticker_info_yahoo(validated)
        logger.info('Source used for info %s: yahoo.', validated)
        return info
    except InvalidTickerError:
        raise
    except (DataUnavailableError, RateLimitedError) as yahoo_exc:
        logger.warning('Yahoo info failed (%s); trying Stooq.', type(yahoo_exc).__name__)
        try:
            out = _fetch_quote_stooq_fallback(validated)
        except (DataUnavailableError, InvalidTickerError) as stooq_exc:
            raise DataUnavailableError(
                f'Quote unavailable for {validated} on Yahoo and Stooq.'
            ) from stooq_exc
        logger.info('Source used for info %s: stooq.', validated)
        return out
