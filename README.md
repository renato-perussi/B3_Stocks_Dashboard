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
   streamlit run streamlit_app.py
   ```

6. **Access the dashboard**
   Open your web browser and navigate to `http://localhost:8501`

---

## Project Structure

The workspace is intentionally lightweight; there are only a handful of Python modules and an `image` folder with a few screenshots and assets. The cache directory is generated automatically when the code runs.

```
B3_Stocks_Dashboard/
├── streamlit_app.py          # Main application entry point
├── services.py               # Business logic and data processing functions
├── config.py                 # Configuration settings and stock lists
├── requirements.txt          # Python dependencies
├── README.md                 # This documentation file
├── image/                    # Assets (screenshots, logos)
│   ├── B3_Logo.png
│   ├── B3_Stocks_Dashboard.png
│   └── B3_Stocks_Dashboard_2.png
└── __pycache__/             # Python bytecode cache (auto-generated)
```

---

## Configuration

### Stocks and Periods

Edit `config.py` to customize the available stocks and time periods:

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

### Core Functions

#### `load_ticker_history(stock_selected, period)`
Loads historical OHLCV data for a specified stock ticker over a given period.

**Parameters:**
- `stock_selected` (str): Stock ticker symbol (e.g., 'PETR4.SA')
- `period` (str): Time period (e.g., '1mo', '1y')

**Returns:**
- `pd.DataFrame`: Historical data with Date, Open, High, Low, Close, Volume columns

---

#### `load_ticker_info_today(stock_selected)`
Retrieves current price data and company information for a stock.

**Parameters:**
- `stock_selected` (str): Stock ticker symbol

**Returns:**
- `dict`: Contains last price, previous close, percentage change, OHLC values, company name, business summary, website, sector, and industry

---

#### `statistics_historical_data(df_stock)`
Calculates statistical metrics from historical stock data.

**Parameters:**
- `df_stock` (pd.DataFrame): DataFrame with historical price data

**Returns:**
- `dict`: Contains volatility, cumulative return, high/low prices, mean, median, standard deviation, and coefficient of variation

---

#### `df_stocks_close(period, stocks_list)`
Fetches closing prices for multiple stocks over a specified period.

**Parameters:**
- `period` (str): Time period for analysis
- `stocks_list` (list): List of stock ticker symbols

**Returns:**
- `pd.DataFrame`: Closing prices with dates as index and tickers as columns

---

#### `df_returns(df_close_prices)`
Calculates daily percentage returns from closing prices.

**Parameters:**
- `df_close_prices` (pd.DataFrame): DataFrame with closing prices

**Returns:**
- `pd.DataFrame`: Daily percentage returns

---

#### `df_stocks_returns_ranking(df_close_returns)`
Ranks stocks by cumulative returns in descending order.

**Parameters:**
- `df_close_returns` (pd.DataFrame): DataFrame with daily returns

**Returns:**
- `pd.DataFrame`: Ranked stocks by cumulative return

---

#### `df_stocks_returns_period(df_close_returns)`
Calculates cumulative returns over time for visualization.

**Parameters:**
- `df_close_returns` (pd.DataFrame): DataFrame with daily returns

**Returns:**
- `pd.DataFrame`: Cumulative returns for each date and stock

---

#### `df_annualized_volatility(df_close_returns)`
Calculates and ranks stocks by annualized volatility (252 trading days).

**Parameters:**
- `df_close_returns` (pd.DataFrame): DataFrame with daily returns

**Returns:**
- `pd.DataFrame`: Stocks ranked by annualized volatility

---

#### `df_coefficient_variation(df_close_prices)`
Calculates and ranks stocks by coefficient of variation (price stability).

**Parameters:**
- `df_close_prices` (pd.DataFrame): DataFrame with closing prices

**Returns:**
- `pd.DataFrame`: Stocks ranked by coefficient of variation

---

## Usage Guide

### 1. Analyze a Single Stock

1. Select a stock ticker from the **Stock Ticker** dropdown in the left panel
2. Choose a time period using the **Period** pills (1mo, 3mo, 6mo, 1y, etc.)
3. View real-time metrics in the top section:
   - Last Price and Daily Change
   - Open Price, Day High, Day Low
   - Previous Close Price
4. Explore the **About** section for company information
5. Review statistical metrics including:
   - Cumulative Return
   - Annualized Volatility
   - Average and Median Prices
   - Coefficient of Variation
6. Analyze the price chart to visualize historical trends

### 2. Compare Multiple Stocks

1. Scroll down to the **Statistical Analyses** section
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

The application implements Streamlit's `@st.cache_data` decorator for data functions to:
- Reduce API calls to yfinance
- Improve dashboard responsiveness
- Cache historical data between reruns

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

1. Add new stocks to `config.py`
2. Create additional analysis functions in `services.py` with appropriate docstrings
3. Integrate new visualizations in `streamlit_app.py`
4. Test functionality with multiple time periods and stock combinations

---

## Requirements

See `requirements.txt` for the complete dependency list. Key packages include:

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **yfinance**: Financial data fetching
- **matplotlib**: Plotting library
- **seaborn**: Statistical data visualization

To install all dependencies:
```bash
pip install pandas streamlit yfinance matplotlib seaborn numpy
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

- **v1.0** (January 2026): Initial release with individual stock analysis, multi-stock comparison, and statistical metrics

---

**Last Updated**: January 2026

