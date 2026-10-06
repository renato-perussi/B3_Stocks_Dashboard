"""App constants and defaults."""

TRADING_DAYS_PER_YEAR: int = 252

# OHLC history: 3600s (1h). Info/quote: 1800s (30min, raised to reduce Yahoo 429).
# Intentional double cache: fetch_history/fetch_close_prices (3600) + stooq (3600).
CACHE_TTL_HISTORY: int = 3600
CACHE_TTL_INFO: int = 1800

DEFAULT_PERIOD: str = '1y'
DEFAULT_STOCK: str = 'PETR4.SA'

PAGE_TITLE: str = 'B3 - Stocks Dashboard'

LOGO_PATH: str = 'docs/screenshots/B3_Logo.png'

CHART_HEIGHT_SINGLE: int = 592
CHART_HEIGHT_COMPARISON: int = 500

CURRENCY_PREFIX: str = 'R$ '
