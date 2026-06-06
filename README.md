# B3 Stocks Dashboard

## Overview

The **B3 Stocks Dashboard** is a comprehensive web-based application for analyzing Brazilian stock market data from the B3 (Brasil, Bolsa, Balcão) exchange. Built with Streamlit, this interactive dashboard provides real-time stock quotes, historical analysis, and comparative metrics for tracking investment performance and market trends.

The application enables investors and analysts to monitor individual stock performance, analyze historical statistics, and conduct portfolio comparisons with detailed visualizations including price charts, correlation heatmaps, and volatility metrics.

<img src="image/B3_Stocks_Dashboard.png">
<img src="image/B3_Stocks_Dashboard_2.png">

---

## Features

### Individual Stock Analysis
- **Real-time Quotes**: Display current prices, daily changes, and opening/closing prices
- **Historical Price Data**: Fetch and visualize Close data
- **Company Information**: Access detailed company profiles, sector classification, and business summaries
- **Statistical Metrics**: Calculate and display key performance indicators including:
  - Cumulative returns
  - Annualized volatility
  - Average and median prices
  - Coefficient of variation

### Multiple Stock Comparison
- **Comparative Returns Analysis**: Track cumulative returns across multiple stocks
- **Correlation Analysis**: Generate correlation matrices with heatmap visualizations
- **Volatility Ranking**: Compare annualized volatility metrics across stocks
- **Variation Coefficient**: Analyze price stability and relative volatility
- **Time-Series Visualization**: View cumulative return trends over selected periods

### Interactive Controls
- **Period Selection**: Choose from multiple timeframes (1 month, 3 months, 6 months, 1 year, 2 years, 5 years, 10 years, YTD)
- **Multi-Select Stocks**: Compare up to multiple stocks simultaneously
- **Real-time Updates**: Automatic data caching for improved performance

### Data Visualization
- Line charts for price trends and cumulative returns
- Bar charts for performance rankings and volatility metrics
- Correlation heatmaps for relationship analysis
- Interactive Streamlit widgets for seamless navigation

---

## Technical Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **Data Source** | yfinance |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn |
| **Programming Language** | Python 3.8+ |

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd B3_Stocks_Dashboard
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

6. **Access the dashboard**
   Open your web browser and navigate to `http://localhost:8501`

---

## Project Structure

The application code is organized as a Python package under `app/`, with a clear separation between data access, analytics and presentation.

```
B3_Stocks_Dashboard/
├── app/
│   ├── main.py                # Application entry point
│   ├── config.py              # PERIODS, STOCKS, STOCKS_DEFAULT
│   ├── constants.py           # TRADING_DAYS_PER_YEAR, cache TTLs, defaults
│   ├── models.py              # Dataclasses: TickerInfo, StockStatistics, ComparisonResult
│   ├── data/
│   │   └── yfinance_client.py # Single point of contact with yfinance
│   ├── analytics/
│   │   ├── statistics.py      # Pure single-stock statistics
│   │   └── comparison.py      # Pure multi-stock comparison analytics
│   ├── errors.py              # Friendly error UI for data failures
│   └── ui/
│       ├── formatters.py      # BRL / percentage display helpers
│       ├── components/        # Reusable Streamlit components
│       │   ├── about_popover.py
│       │   ├── comparison_controls.py
│       │   ├── correlation_heatmap.py
│       │   ├── cumulative_returns_chart.py
│       │   ├── header.py
│       │   ├── horizontal_bar.py
│       │   ├── price_chart.py
│       │   ├── statistics_panel.py
│       │   └── ticker_metrics_row.py
│       └── views/             # Composed views
│           ├── single_stock_view.py
│           └── comparison_view.py
├── .streamlit/
│   └── config.toml
├── image/                     # Assets (screenshots, logos)
├── pyproject.toml             # Tooling config (ruff, mypy) and project metadata
├── requirements.txt           # Runtime dependencies
├── requirements-dev.txt       # Development dependencies (ruff, mypy)
└── README.md
```

---

## Configuration

### Stocks and Periods

Edit `app/config.py` to customize the available stocks and time periods:

#### Available Periods
```python
PERIODS = ['1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd']
```

#### Default Stocks (Quick Analysis)
```python
STOCKS_DEFAULT = [
    'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 
    'BBAS3.SA', 'ABEV3.SA', 'BBDC4.SA'
]
```

#### Complete Stock List
The `STOCKS` list contains 88 companies from the IBOVESPA index (January 2026), including:
- Energy: PETR4.SA, VALE3.SA
- Banking: ITUB4.SA, BBAS3.SA, BBDC4.SA
- Consumer Goods: ABEV3.SA
- Utilities: CMIG4.SA, CPLE3.SA
- And many more...

**Note**: All stock tickers must include the `.SA` suffix for B3 listed companies.

---

## API Reference

### Domain Models (`app/models.py`)

- **`TickerInfo`** — real-time quote and company profile fields.
- **`StockStatistics`** — period statistics (volatility, return, prices, etc.).
- **`ComparisonResult`** — bundle of DataFrames produced for a multi-stock analysis.

### Data Layer (`app/data/yfinance_client.py`)

#### `fetch_history(ticker, period)`
Loads OHLCV history for a single ticker. Cached by Streamlit.

#### `fetch_close_prices(period, tickers)`
Loads close prices for multiple tickers aligned by date.

#### `fetch_ticker_info(ticker)`
Returns a `TickerInfo` dataclass with quote and company data. Cached with a 5-minute TTL.

### Analytics Layer (`app/analytics/`)

#### `calculate_statistics(history) -> StockStatistics`
Computes the eight statistics from an OHLCV history frame.

#### `calculate_returns(close_prices) -> DataFrame`
Daily percentage returns, first row zero-filled.

#### `cumulative_returns_period(returns) -> DataFrame`
Cumulative returns over time, in percent.

#### `cumulative_returns_ranking(returns) -> DataFrame`
Total cumulative return per ticker, sorted descending.

#### `annualized_volatility(returns) -> DataFrame`
Annualized volatility per ticker, sorted descending.

#### `coefficient_variation(close_prices) -> DataFrame`
Coefficient of variation per ticker, sorted descending.

---

## Usage Guide

### 1. Analyze a Single Stock (Tab 1)

The dashboard opens with the B3 logo at the top and two tabs: **Single Stock** and **Multiple Stocks**.

1. Open the **Single Stock** tab
2. Select a stock ticker from the **Stock Ticker** dropdown in the left panel
3. Choose a time period using the **Period** pills (1mo, 3mo, 6mo, 1y, etc.)
4. View real-time metrics in the top section:
   - Last Price and Daily Change
   - Open Price, Day High, Day Low
   - Previous Close Price
5. Explore the **About** section for company information
6. Review statistical metrics including:
   - Cumulative Return
   - Annualized Volatility
   - Average and Median Prices
   - Coefficient of Variation
7. Analyze the price chart to visualize historical trends

### 2. Compare Multiple Stocks (Tab 2)

1. Open the **Multiple Stocks** tab
2. Select a time period for comparison
3. Choose **at least two stocks** from the multiselect box
4. View automatically generated analyses:
   - **Cumulative Returns Chart**: Track return trends over time
   - **Correlation Heatmap**: Identify relationships between stocks (1.0 = perfect correlation, -1.0 = inverse correlation, 0 = no correlation)
   - **Returns Ranking**: Bar chart showing cumulative returns ranked
   - **Volatility Metrics**: Compare annualized volatility across stocks
   - **Coefficient Variation**: Identify stocks with stable vs. volatile prices

### 3. Interpret Key Metrics

- **Cumulative Return**: Total percentage gain/loss over the period
- **Annualized Volatility**: Standard deviation of returns scaled to 1 year (252 trading days)
- **Coefficient of Variation**: Risk per unit of return (lower = more stable)
- **Correlation**: Relationship between stock price movements
  - Close to 1: Stocks move together
  - Close to -1: Stocks move in opposite directions
  - Close to 0: No linear relationship

---

## Performance Optimization

The application implements Streamlit's `@st.cache_data` decorator for the data layer to:
- Reduce API calls to yfinance
- Improve dashboard responsiveness
- Cache historical data between reruns
- Refresh quote data every 5 minutes (`CACHE_TTL_INFO`)

---

## Data Source

- **Primary Source**: [yfinance](https://finance.yahoo.com/) - Yahoo Finance API
- **Market**: B3 (Brasil, Bolsa, Balcão)
- **Data Type**: Historical OHLCV prices and current quotes
- **Update Frequency**: Real-time (subject to market hours and data provider updates)

---

## Limitations

1. **Market Hours**: Historical data updates occur during B3 trading hours
2. **Delisted Stocks**: Stocks that have been delisted may return incomplete data
3. **API Rate Limiting**: Yahoo Finance has rate limits; excessive requests may result in temporary blocks
4. **Historical Data**: Complete historical data availability varies by stock (typically 10+ years)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **"Please select at least two stocks for analysis"** | Select 2 or more stocks in the multiselect box for comparative analysis |
| **Missing price data** | Some stocks may have gaps in historical data; try a different period or stock |
| **Slow dashboard loading** | Clear Streamlit cache: Press `C` in the app or restart with `streamlit run --logger.level=debug streamlit_app.py` |
| **Connection errors** | Check internet connection and verify yfinance API availability |
| **Stock not found** | Ensure the ticker includes `.SA` suffix (e.g., 'PETR4.SA' not 'PETR4') |

---

## Contributing

To extend or modify the dashboard:

1. Add new stocks to `app/config.py`
2. Add new analytics functions under `app/analytics/`
3. Add new Streamlit components under `app/ui/components/`
4. Compose new views in `app/ui/views/` and call them from `app/main.py`
5. Test functionality with multiple time periods and stock combinations

### Development

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the linter and formatter:

```bash
ruff check .
ruff format .
```

Run static type checking:

```bash
mypy app/
```

---

## Requirements

See `requirements.txt` for the complete runtime dependency list. Key packages include:

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **yfinance**: Financial data fetching
- **matplotlib**: Plotting library
- **seaborn**: Statistical data visualization

To install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Future Enhancements

Potential features for future versions:

- Real-time alerts for price thresholds
- Portfolio optimization recommendations
- Technical indicators (Moving Averages, RSI, MACD)
- Machine learning-based price predictions
- Export reports to PDF/Excel
- User authentication and saved preferences
- Mobile-responsive design improvements
- Historical correlation analysis
- Risk assessment dashboard

---

## License

This project is developed for educational and analytical purposes. Users are responsible for verifying data accuracy and conducting independent due diligence before making investment decisions.

---

## Support & Contact

For issues, feature requests, or questions:
1. Check the Troubleshooting section above
2. Verify your dependencies are correctly installed
3. Ensure your internet connection is stable
4. Review the API Reference for function usage

---

## Disclaimer

This dashboard is provided for informational and analytical purposes only. It should not be considered as financial advice. Always conduct thorough research and consult with qualified financial professionals before making investment decisions. Past performance does not guarantee future results. The creators of this application are not responsible for any financial losses resulting from use of this tool.

---

## Version History

- **v1.1** (June 2026): Refactored into a layered `app/` package with dataclass models, dedicated data and analytics layers, reusable UI components, error handling, and tooling (ruff + mypy).
- **v1.0** (January 2026): Initial release with individual stock analysis, multi-stock comparison, and statistical metrics

---

**Last Updated**: June 2026

