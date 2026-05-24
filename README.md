# Real-Time JSE Financial Market Database System

## Project Overview

The Real-Time JSE Financial Market Database System is an end-to-end financial analytics platform designed to collect, process, store, and visualize Johannesburg Stock Exchange (JSE) market data.

The system extracts stock market data from Yahoo Finance using Python ETL pipelines, stores the data in a normalized SQL Server database, calculates technical indicators for financial analysis, and provides interactive dashboards using Streamlit and Plotly.

This project demonstrates skills in:

- Data Engineering
- Database Design
- Financial Analytics
- Python Automation
- SQL Development
- Dashboard Development
- ETL Pipeline Development

---

# Technologies Used

- Python
- SQL Server
- pyodbc
- pandas
- NumPy
- yfinance API
- Streamlit
- Plotly
- SQL Stored Procedures

---

# Key Features

## Data Engineering & ETL
- Automated extraction of JSE stock data from Yahoo Finance
- ETL pipelines for data extraction, transformation, and loading
- Automated duplicate handling and validation checks
- OHLC price consistency validation
- Missing date handling

## Database Design
- Normalized SQL Server relational database (3NF)
- Structured schema for financial market analytics
- Optimized relationships using primary and foreign keys

## Financial Analytics
- Technical indicators:
  - SMA20
  - SMA50
  - RSI14
  - MACD
- 52-week high/low calculations
- Moving average crossover trading signals
- Top gainers and losers analysis
- Volatility and return analytics

## Interactive Dashboard
- Real-time financial market dashboard
- Interactive filtering by stock and date range
- Candlestick charts
- Technical indicator visualizations
- Trading signal analysis
- Market watchlist
- Dynamic styling for gains/losses

---

# Database Schema

## Tables

### Market.Sectors
Stores financial market sectors.

### Market.Companies
Stores JSE-listed company information.

### Market.CalendarDates
Stores trading calendar dates.

### Market.StockPrices
Stores historical stock market OHLCV data.

### Market.TechnicalIndicators
Stores calculated technical indicators.

---

# Project Structure

```text
Real-Time-Financial-Market-System/
│
├── config.py
├── setup_database.py
├── fetch_stock_data.py
├── calculate_indicators.py
├── run_etl.py
├── dashboard.py
├── requirements1.txt
├── README.md
│
└── screenshots/
```

---

# Dashboard Features

## Market Overview
- Top gainers
- Most active stocks
- Volume distribution

## Market Watchlist
- Open price
- High price
- Low price
- Close price
- 52-week high/low
- Percentage movement indicators

## Stock Analysis
- Interactive candlestick charts
- Historical price analysis

## Technical Indicators
- SMA20 and SMA50
- RSI14
- MACD analysis

## Trading Signals
- Moving average crossover signals
- Buy/Sell/Hold indicators

---

# How to Run the Project

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/financial-market-dashboard.git

cd financial-market-dashboard
```

---

## 2. Install Dependencies

```bash
pip install -r requirements1.txt
```

---

## 3. Configure SQL Server

Update `config.py` with your SQL Server configuration.

Example:

```python
SERVER = "localhost\\SQLEXPRESS"
DATABASE = "FinancialMarketDB"
```

---

## 4. Create Database and Tables

```bash
python setup_database.py
```

---

## 5. Run ETL Pipeline

```bash
python run_etl.py
```

---

## 6. Launch Dashboard

```bash
python -m streamlit run dashboard.py
```

---

# Example Dashboard Screens

- Market Watchlist
- Technical Indicators
- Trading Signals
- Candlestick Charts
- Market Analytics

---

# Future Improvements

- Live streaming market data
- Portfolio optimization
- Risk analytics
- Sharpe ratio analysis
- Bollinger Bands
- ATR indicator
- Machine learning price forecasting
- Cloud deployment
- Real-time alert notifications

---

# Skills Demonstrated

- Python Programming
- SQL Server Development
- ETL Pipeline Engineering
- Financial Data Analytics
- Data Validation
- Dashboard Development
- Technical Indicator Development
- Database Normalization
- API Integration
- Data Visualization

---

# Author

**Matlhomola Mohlala**

- Data Analytics & Data Science
- Financial Analytics
- Data Engineering
- Machine Learning

```
