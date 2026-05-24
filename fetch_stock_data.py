# fetch_stock_data.py

import pyodbc
import yfinance as yf
from datetime import datetime, timedelta
from config import CONNECTION_STRING, JSE_TICKERS


def fix_price_data(row):
    open_price = float(row["Open"])
    high_price = float(row["High"])
    low_price = float(row["Low"])
    close_price = float(row["Close"])
    volume = int(row["Volume"])

    high_price = max(high_price, open_price, close_price)
    low_price = min(low_price, open_price, close_price)

    return open_price, high_price, low_price, close_price, volume


def get_or_create_date(cursor, trade_date):
    cursor.execute("""
        SELECT DateID
        FROM Market.CalendarDates
        WHERE [Date] = ?
    """, trade_date)

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute("""
        INSERT INTO Market.CalendarDates
        ([Date], DayOfWeek, [Month], [Quarter], [Year], IsTradingDay)
        OUTPUT INSERTED.DateID
        VALUES (?, DATEPART(dw, ?), MONTH(?), DATEPART(q, ?), YEAR(?), 1)
    """, trade_date, trade_date, trade_date, trade_date, trade_date)

    return cursor.fetchone()[0]


def fetch_and_store_stock_data(ticker, years=1):
    print(f"\nProcessing {ticker}...")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)

    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)

    if data.empty:
        print(f"No data found for {ticker}.")
        return 0

    conn = pyodbc.connect(CONNECTION_STRING)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT CompanyID
        FROM Market.Companies
        WHERE Ticker = ?
    """, ticker)

    company = cursor.fetchone()

    if not company:
        print(f"Company {ticker} not found in database.")
        conn.close()
        return 0

    company_id = company[0]
    inserted = 0
    skipped = 0

    for index, row in data.iterrows():
        trade_date = index.date()
        date_id = get_or_create_date(cursor, trade_date)

        cursor.execute("""
            SELECT PriceID
            FROM Market.StockPrices
            WHERE CompanyID = ? AND DateID = ?
        """, company_id, date_id)

        if cursor.fetchone():
            skipped += 1
            continue

        open_price, high_price, low_price, close_price, volume = fix_price_data(row)

        try:
            cursor.execute("""
                INSERT INTO Market.StockPrices
                (CompanyID, DateID, OpenPrice, HighPrice, LowPrice, ClosePrice, Volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, company_id, date_id, open_price, high_price, low_price, close_price, volume)

            inserted += 1

        except Exception as e:
            print(f"Could not insert {ticker} for {trade_date}: {e}")

    conn.commit()
    conn.close()

    print(f"{ticker}: inserted {inserted}, skipped {skipped}.")
    return inserted


def fetch_all_stocks():
    total = 0

    for ticker in JSE_TICKERS:
        total += fetch_and_store_stock_data(ticker, years=1)

    print(f"\nTotal new records inserted: {total}")


if __name__ == "__main__":
    fetch_all_stocks()
