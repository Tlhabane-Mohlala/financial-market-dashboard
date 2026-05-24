# calculate_indicators.py

import pyodbc
import pandas as pd
from config import CONNECTION_STRING, JSE_TICKERS


def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def get_stock_prices(cursor, ticker):
    query = """
    SELECT
        c.CompanyID,
        cd.DateID,
        cd.Date,
        sp.ClosePrice
    FROM Market.StockPrices sp
    JOIN Market.Companies c
        ON sp.CompanyID = c.CompanyID
    JOIN Market.CalendarDates cd
        ON sp.DateID = cd.DateID
    WHERE c.Ticker = ?
    ORDER BY cd.Date
    """

    return pd.read_sql(query, cursor.connection, params=[ticker])


def calculate_and_store_indicators(ticker):
    print(f"\nCalculating indicators for {ticker}...")

    conn = pyodbc.connect(CONNECTION_STRING)
    cursor = conn.cursor()

    df = get_stock_prices(cursor, ticker)

    if df.empty:
        print(f"No price data found for {ticker}.")
        conn.close()
        return

    df["ClosePrice"] = df["ClosePrice"].astype(float)

    df["SMA20"] = df["ClosePrice"].rolling(window=20).mean()
    df["SMA50"] = df["ClosePrice"].rolling(window=50).mean()
    df["RSI14"] = calculate_rsi(df["ClosePrice"], period=14)

    ema12 = df["ClosePrice"].ewm(span=12, adjust=False).mean()
    ema26 = df["ClosePrice"].ewm(span=26, adjust=False).mean()

    df["MACDLine"] = ema12 - ema26
    df["MACDSignal"] = df["MACDLine"].ewm(span=9, adjust=False).mean()
    df["MACDHistogram"] = df["MACDLine"] - df["MACDSignal"]

    inserted = 0
    updated = 0

    for _, row in df.iterrows():
        company_id = int(row["CompanyID"])
        date_id = int(row["DateID"])

        values = [
            None if pd.isna(row["SMA20"]) else float(row["SMA20"]),
            None if pd.isna(row["SMA50"]) else float(row["SMA50"]),
            None if pd.isna(row["RSI14"]) else float(row["RSI14"]),
            None if pd.isna(row["MACDLine"]) else float(row["MACDLine"]),
            None if pd.isna(row["MACDSignal"]) else float(row["MACDSignal"]),
            None if pd.isna(row["MACDHistogram"]) else float(row["MACDHistogram"])
        ]

        cursor.execute("""
            SELECT IndicatorID
            FROM Market.TechnicalIndicators
            WHERE CompanyID = ? AND DateID = ?
        """, company_id, date_id)

        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE Market.TechnicalIndicators
                SET
                    SMA20 = ?,
                    SMA50 = ?,
                    RSI14 = ?,
                    MACDLine = ?,
                    MACDSignal = ?,
                    MACDHistogram = ?
                WHERE CompanyID = ?
                AND DateID = ?
            """, *values, company_id, date_id)

            updated += 1

        else:
            cursor.execute("""
                INSERT INTO Market.TechnicalIndicators
                (
                    CompanyID,
                    DateID,
                    SMA20,
                    SMA50,
                    RSI14,
                    MACDLine,
                    MACDSignal,
                    MACDHistogram
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, company_id, date_id, *values)

            inserted += 1

    conn.commit()
    conn.close()

    print(f"{ticker}: inserted {inserted}, updated {updated} indicator records.")


def calculate_all_indicators():
    for ticker in JSE_TICKERS:
        calculate_and_store_indicators(ticker)


if __name__ == "__main__":
    calculate_all_indicators()
