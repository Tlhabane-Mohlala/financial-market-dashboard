# Real-Time JSE Financial Market Database System

## Project Overview

This project is an end-to-end financial market database and dashboard system. It extracts JSE stock market data from Yahoo Finance, stores it in a normalized SQL Server database, calculates technical indicators, and visualizes the results using Streamlit.

## Technologies Used

- Python
- SQL Server
- pyodbc
- pandas
- yfinance
- Streamlit
- Plotly
- schedule

## Key Features

- Normalized database schema
- Stock price extraction from Yahoo Finance
- Automated ETL pipeline
- Data validation and duplicate handling
- Technical indicators: SMA20, SMA50, RSI14, MACD
- Stored procedures for financial analysis
- Streamlit dashboard for real-time monitoring

## Database Tables

- Market.Sectors
- Market.Companies
- Market.CalendarDates
- Market.StockPrices
- Market.TechnicalIndicators

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
