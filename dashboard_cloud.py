import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


st.set_page_config(
    page_title="JSE Financial Dashboard",
    page_icon="📈",
    layout="wide"
)


@st.cache_data(ttl=300)
def load_data():
    companies = pd.read_csv("Data/Companies.csv")
    sectors = pd.read_csv("Data/Sectors.csv")
    dates = pd.read_csv("Data/CalendarDates.csv")
    prices = pd.read_csv("Data/StockPrices.csv")
    indicators = pd.read_csv("Data/TechnicalIndicators.csv")

    dates["Date"] = pd.to_datetime(dates["Date"])

    indicators = indicators[
        [
            "CompanyID",
            "DateID",
            "SMA20",
            "SMA50",
            "RSI14",
            "MACDLine",
            "MACDSignal",
            "MACDHistogram",
        ]
    ]

    df = prices.merge(companies, on="CompanyID", how="left")
    df = df.merge(sectors, on="SectorID", how="left")
    df = df.merge(dates, on="DateID", how="left")
    df = df.merge(indicators, on=["CompanyID", "DateID"], how="left")

    return df


def format_change(value):
    if pd.isna(value):
        return "N/A"
    if value > 0:
        return f"▲ +{value:.2f}%"
    if value < 0:
        return f"▼ {value:.2f}%"
    return f"{value:.2f}%"


def style_change(value):
    value = str(value)
    if "▲" in value:
        return "color: green; font-weight: bold;"
    if "▼" in value:
        return "color: red; font-weight: bold;"
    return ""


def get_companies():
    return (
        df[["CompanyID", "Ticker", "CompanyName"]]
        .drop_duplicates()
        .sort_values("Ticker")
    )


def get_latest_prices():
    latest = (
        df.sort_values("Date")
        .groupby("Ticker")
        .tail(1)
        .copy()
    )

    return latest[
        [
            "Ticker",
            "CompanyName",
            "SectorName",
            "ClosePrice",
            "Volume",
            "Date",
        ]
    ].sort_values("Volume", ascending=False)


def get_market_watchlist():
    latest = (
        df.sort_values("Date")
        .groupby("Ticker")
        .tail(1)
        .copy()
    )

    previous = (
        df.sort_values("Date")
        .groupby("Ticker")
        .nth(-2)
        .reset_index()
    )

    latest = latest.merge(
        previous[["Ticker", "ClosePrice"]],
        on="Ticker",
        how="left",
        suffixes=("", "_Previous"),
    )

    latest["ChangePercent"] = (
        (latest["ClosePrice"] - latest["ClosePrice_Previous"])
        / latest["ClosePrice_Previous"]
    ) * 100

    high_low = df.groupby("Ticker").agg(
        High52Week=("HighPrice", "max"),
        Low52Week=("LowPrice", "min"),
    ).reset_index()

    latest = latest.merge(high_low, on="Ticker", how="left")

    return latest[
        [
            "Ticker",
            "CompanyName",
            "SectorName",
            "OpenPrice",
            "HighPrice",
            "LowPrice",
            "ClosePrice",
            "Volume",
            "High52Week",
            "Low52Week",
            "ChangePercent",
        ]
    ].sort_values("ChangePercent", ascending=False)


def get_stock_history(ticker, days):
    latest_date = df["Date"].max()
    start_date = latest_date - pd.Timedelta(days=days)

    stock_data = df[
        (df["Ticker"] == ticker)
        & (df["Date"] >= start_date)
    ].sort_values("Date")

    return stock_data[
        [
            "Date",
            "OpenPrice",
            "HighPrice",
            "LowPrice",
            "ClosePrice",
            "Volume",
            "SMA20",
            "SMA50",
            "RSI14",
            "MACDLine",
            "MACDSignal",
            "MACDHistogram",
        ]
    ]


def get_top_gainers():
    latest = (
        df.sort_values("Date")
        .groupby("Ticker")
        .tail(1)
        .copy()
    )

    previous = (
        df.sort_values("Date")
        .groupby("Ticker")
        .nth(-2)
        .reset_index()
    )

    gainers = latest.merge(
        previous[["Ticker", "ClosePrice"]],
        on="Ticker",
        how="left",
        suffixes=("", "_Previous"),
    )

    gainers["DailyReturn"] = (
        (gainers["ClosePrice"] - gainers["ClosePrice_Previous"])
        / gainers["ClosePrice_Previous"]
    ) * 100

    gainers = gainers[
        [
            "Ticker",
            "CompanyName",
            "ClosePrice",
            "DailyReturn",
        ]
    ]

    gainers = gainers.rename(
        columns={"ClosePrice": "CurrentPrice"}
    )

    return gainers.sort_values("DailyReturn", ascending=False).head(3)


def get_signals():
    latest = (
        df.sort_values("Date")
        .groupby("Ticker")
        .tail(1)
        .copy()
    )

    signals = latest[
        [
            "Ticker",
            "Date",
            "SMA20",
            "SMA50",
        ]
    ].copy()

    signals["Signal"] = signals.apply(
        lambda row: "BUY SIGNAL"
        if row["SMA20"] > row["SMA50"]
        else "SELL SIGNAL"
        if row["SMA20"] < row["SMA50"]
        else "HOLD",
        axis=1,
    )

    return signals


df = load_data()


def main():
    st.title("📈 JSE Financial Market Dashboard")

    st.markdown("""
    Real-time financial market monitoring dashboard
    using Python, SQL Server and Streamlit.
    """)

    companies = get_companies()

    if companies.empty:
        st.warning("No companies found.")
        return

    st.sidebar.header("Dashboard Controls")

    selected_ticker = st.sidebar.selectbox(
        "Select Stock",
        companies["Ticker"].tolist()
    )

    date_range = st.sidebar.selectbox(
        "Select Date Range",
        [
            "7 Days",
            "30 Days",
            "90 Days",
            "1 Year",
        ],
        index=2,
    )

    days_map = {
        "7 Days": 7,
        "30 Days": 30,
        "90 Days": 90,
        "1 Year": 365,
    }

    days = days_map[date_range]

    if st.sidebar.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    latest_prices = get_latest_prices()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Companies", len(companies))

    with col2:
        avg_price = (
            latest_prices["ClosePrice"].mean()
            if not latest_prices.empty
            else 0
        )
        st.metric("Average Price", f"R{avg_price:,.2f}")

    with col3:
        total_volume = (
            latest_prices["Volume"].sum()
            if not latest_prices.empty
            else 0
        )
        st.metric("Total Volume", f"{total_volume:,.0f}")

    with col4:
        last_date = (
            latest_prices["Date"].max()
            if not latest_prices.empty
            else "N/A"
        )
        st.metric("Latest Date", str(last_date.date() if hasattr(last_date, "date") else last_date))

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Market Overview",
        "Market Watchlist",
        "Stock Analysis",
        "Technical Indicators",
        "Trading Signals",
        "Range High/Low",
    ])

    with tab1:
        st.subheader("Market Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Top Gainers")

            gainers = get_top_gainers()

            if not gainers.empty:
                fig = px.bar(
                    gainers,
                    x="Ticker",
                    y="DailyReturn",
                    text="DailyReturn",
                    title="Top 3 Gainers",
                )

                fig.update_traces(
                    textposition=["inside", "outside", "outside"],
                    texttemplate="%{text:.2f}",
                    textfont_size=12,
                    cliponaxis=False,
                )

                fig.update_layout(
                    xaxis_title="Ticker",
                    yaxis_title="DailyReturn",
                    height=420,
                    showlegend=False,
                    bargap=0.25,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis=dict(
                        categoryorder="array",
                        categoryarray=gainers["Ticker"].tolist(),
                    ),
                )

                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(gainers, use_container_width=True)

            else:
                st.info("No gainers data available.")

        with col2:
            st.markdown("### Most Active Stocks")

            if not latest_prices.empty:
                fig = px.pie(
                    latest_prices,
                    values="Volume",
                    names="Ticker",
                    title="Volume Distribution",
                )

                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(latest_prices, use_container_width=True)

            else:
                st.info("No volume data available.")

    with tab2:
        st.subheader("Market Watchlist")

        watchlist = get_market_watchlist()

        if not watchlist.empty:
            display_watchlist = watchlist.copy()

            display_watchlist["ChangePercent"] = display_watchlist[
                "ChangePercent"
            ].apply(format_change)

            styled_watchlist = display_watchlist.style.format({
                "OpenPrice": "R{:,.2f}",
                "HighPrice": "R{:,.2f}",
                "LowPrice": "R{:,.2f}",
                "ClosePrice": "R{:,.2f}",
                "Volume": "{:,.0f}",
                "High52Week": "R{:,.2f}",
                "Low52Week": "R{:,.2f}",
            }).map(
                lambda value: "color: green; font-weight: bold;",
                subset=["HighPrice", "High52Week"],
            ).map(
                lambda value: "color: red; font-weight: bold;",
                subset=["LowPrice", "Low52Week"],
            ).map(
                style_change,
                subset=["ChangePercent"],
            )

            st.dataframe(styled_watchlist, use_container_width=True)

        else:
            st.info("No market watchlist data available.")

    with tab3:
        st.subheader(f"Stock Analysis: {selected_ticker}")

        stock_data = get_stock_history(selected_ticker, days)

        if not stock_data.empty:
            fig = go.Figure()

            fig.add_trace(go.Candlestick(
                x=stock_data["Date"],
                open=stock_data["OpenPrice"],
                high=stock_data["HighPrice"],
                low=stock_data["LowPrice"],
                close=stock_data["ClosePrice"],
                name="OHLC",
            ))

            fig.update_layout(
                title=f"{selected_ticker} Candlestick Chart",
                xaxis_title="Date",
                yaxis_title="Price",
                height=500,
            )

            st.plotly_chart(fig, use_container_width=True)

            latest = stock_data.iloc[-1]

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Close Price", f"R{latest['ClosePrice']:,.2f}")
            c2.metric("High Price", f"R{latest['HighPrice']:,.2f}")
            c3.metric("Low Price", f"R{latest['LowPrice']:,.2f}")
            c4.metric("Volume", f"{latest['Volume']:,.0f}")

        else:
            st.warning("No stock data found.")

    with tab4:
        st.subheader(f"Technical Indicators: {selected_ticker}")

        stock_data = get_stock_history(selected_ticker, days)

        if not stock_data.empty:
            fig_ma = go.Figure()

            fig_ma.add_trace(go.Scatter(
                x=stock_data["Date"],
                y=stock_data["ClosePrice"],
                name="Close Price",
            ))

            fig_ma.add_trace(go.Scatter(
                x=stock_data["Date"],
                y=stock_data["SMA20"],
                name="SMA 20",
            ))

            fig_ma.add_trace(go.Scatter(
                x=stock_data["Date"],
                y=stock_data["SMA50"],
                name="SMA 50",
            ))

            fig_ma.update_layout(
                title="Moving Averages",
                xaxis_title="Date",
                yaxis_title="Price",
                height=400,
            )

            st.plotly_chart(fig_ma, use_container_width=True)

            fig_rsi = go.Figure()

            fig_rsi.add_trace(go.Scatter(
                x=stock_data["Date"],
                y=stock_data["RSI14"],
                name="RSI 14",
            ))

            fig_rsi.add_hline(y=70, line_dash="dash")
            fig_rsi.add_hline(y=30, line_dash="dash")
            fig_rsi.update_layout(title="RSI Indicator", height=350)

            st.plotly_chart(fig_rsi, use_container_width=True)

            fig_macd = go.Figure()

            fig_macd.add_trace(go.Scatter(
                x=stock_data["Date"],
                y=stock_data["MACDLine"],
                name="MACD Line",
            ))

            fig_macd.add_trace(go.Scatter(
                x=stock_data["Date"],
                y=stock_data["MACDSignal"],
                name="Signal Line",
            ))

            fig_macd.add_trace(go.Bar(
                x=stock_data["Date"],
                y=stock_data["MACDHistogram"],
                name="Histogram",
            ))

            fig_macd.update_layout(title="MACD Indicator", height=350)

            st.plotly_chart(fig_macd, use_container_width=True)

        else:
            st.warning("No indicators available.")

    with tab5:
        st.subheader("Moving Average Trading Signals")

        signals = get_signals()

        if not signals.empty:
            st.dataframe(signals, use_container_width=True)

            buy_count = len(signals[signals["Signal"].str.contains("BUY", na=False)])
            sell_count = len(signals[signals["Signal"].str.contains("SELL", na=False)])
            hold_count = len(signals[signals["Signal"].str.contains("HOLD", na=False)])

            c1, c2, c3 = st.columns(3)

            c1.metric("Buy Signals", buy_count)
            c2.metric("Sell Signals", sell_count)
            c3.metric("Hold Signals", hold_count)

        else:
            st.info("No trading signals available.")

    with tab6:
        st.subheader(f"{date_range} High/Low: {selected_ticker}")

        stock_data = get_stock_history(selected_ticker, days)

        if not stock_data.empty:
            high_value = stock_data["HighPrice"].max()
            low_value = stock_data["LowPrice"].min()

            c1, c2 = st.columns(2)

            c1.metric(f"{date_range} High", f"R{high_value:,.2f}")
            c2.metric(f"{date_range} Low", f"R{low_value:,.2f}")

            fig_range = go.Figure()

            fig_range.add_trace(go.Scatter(
                x=stock_data["Date"],
                y=stock_data["HighPrice"],
                name="High Price",
            ))

            fig_range.add_trace(go.Scatter(
                x=stock_data["Date"],
                y=stock_data["LowPrice"],
                name="Low Price",
            ))

            fig_range.update_layout(
                title=f"{selected_ticker} High vs Low",
                xaxis_title="Date",
                yaxis_title="Price",
                height=400,
            )

            st.plotly_chart(fig_range, use_container_width=True)

            st.dataframe(
                stock_data[
                    [
                        "Date",
                        "OpenPrice",
                        "HighPrice",
                        "LowPrice",
                        "ClosePrice",
                        "Volume",
                    ]
                ],
                use_container_width=True,
            )

        else:
            st.info("No data available.")

    st.markdown("---")

    st.markdown(
        """
        <div style='text-align: center; padding-top: 20px; font-size:18px; color: gray;'>
            Prepared by <b>M. Mohlala</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Last refreshed: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
