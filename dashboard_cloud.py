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


df = load_data()

st.title("📈 JSE Financial Market Dashboard")

st.markdown(
    "Real-time financial market monitoring dashboard using Python, SQL Server and Streamlit."
)

companies = sorted(df["Ticker"].dropna().unique())

st.sidebar.header("Dashboard Controls")

selected_ticker = st.sidebar.selectbox(
    "Select Stock",
    companies
)

date_range = st.sidebar.selectbox(
    "Select Date Range",
    ["7 Days", "30 Days", "90 Days", "1 Year"],
    index=2
)

days_map = {
    "7 Days": 7,
    "30 Days": 30,
    "90 Days": 90,
    "1 Year": 365
}

days = days_map[date_range]

latest_date = df["Date"].max()
start_date = latest_date - pd.Timedelta(days=days)

filtered_df = df[df["Date"] >= start_date]

selected_df = filtered_df[
    filtered_df["Ticker"] == selected_ticker
].sort_values("Date")

latest_prices = (
    df.sort_values("Date")
    .groupby("Ticker")
    .tail(1)
    .copy()
)

previous_prices = (
    df.sort_values("Date")
    .groupby("Ticker")
    .nth(-2)
    .reset_index()
)

latest_prices = latest_prices.merge(
    previous_prices[["Ticker", "ClosePrice"]],
    on="Ticker",
    how="left",
    suffixes=("", "_Previous")
)

latest_prices["ChangePercent"] = (
    (latest_prices["ClosePrice"] - latest_prices["ClosePrice_Previous"])
    / latest_prices["ClosePrice_Previous"]
) * 100

high_low = df.groupby("Ticker").agg(
    High52Week=("HighPrice", "max"),
    Low52Week=("LowPrice", "min")
).reset_index()

latest_prices = latest_prices.merge(
    high_low,
    on="Ticker",
    how="left"
)

# Top gainers logic similar to SQL stored procedure
price_changes = df.sort_values(["Ticker", "Date"]).copy()

price_changes["PreviousPrice"] = price_changes.groupby("Ticker")[
    "ClosePrice"
].shift(1)

price_changes["DailyReturn"] = (
    (price_changes["ClosePrice"] - price_changes["PreviousPrice"])
    / price_changes["PreviousPrice"]
) * 100

gainers = (
    price_changes[price_changes["PreviousPrice"].notna()]
    .sort_values("DailyReturn", ascending=False)
    .head(5)
)

signals = latest_prices[
    [
        "Ticker",
        "Date",
        "SMA20",
        "SMA50"
    ]
].copy()

signals["Signal"] = signals.apply(
    lambda row: "BUY SIGNAL"
    if row["SMA20"] > row["SMA50"]
    else "SELL SIGNAL"
    if row["SMA20"] < row["SMA50"]
    else "HOLD",
    axis=1
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Companies",
        len(companies)
    )

with col2:
    avg_price = latest_prices["ClosePrice"].mean()
    st.metric(
        "Average Price",
        f"R{avg_price:,.2f}"
    )

with col3:
    total_volume = latest_prices["Volume"].sum()
    st.metric(
        "Total Volume",
        f"{total_volume:,.0f}"
    )

with col4:
    st.metric(
        "Latest Date",
        str(latest_date.date())
    )


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Market Overview",
    "Market Watchlist",
    "Stock Analysis",
    "Technical Indicators",
    "Trading Signals",
    "Range High/Low"
])


with tab1:
    st.subheader("Market Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Top Gainers")

        if not gainers.empty:
            fig = px.bar(
                gainers,
                x="Ticker",
                y="DailyReturn",
                text="DailyReturn",
                title="Top 5 Daily Gainers (%)"
            )

            fig.update_traces(
                texttemplate="%{text:.2f}",
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Ticker",
                yaxis_title="DailyReturn",
                height=420,
                xaxis={
                    "categoryorder": "array",
                    "categoryarray": gainers["Ticker"].tolist()
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.dataframe(
                gainers[
                    [
                        "Ticker",
                        "CompanyName",
                        "ClosePrice",
                        "DailyReturn"
                    ]
                ],
                use_container_width=True
            )

        else:
            st.info("No gainers data available.")

    with col2:
        st.markdown("### Most Active Stocks")

        if not latest_prices.empty:
            fig = px.pie(
                latest_prices,
                values="Volume",
                names="Ticker",
                title="Volume Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.dataframe(
                latest_prices[
                    [
                        "Ticker",
                        "CompanyName",
                        "SectorName",
                        "ClosePrice",
                        "Volume",
                        "Date"
                    ]
                ],
                use_container_width=True
            )

        else:
            st.info("No volume data available.")


with tab2:
    st.subheader("Market Watchlist")

    watchlist = latest_prices[
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
            "ChangePercent"
        ]
    ].copy()

    watchlist["ChangePercent"] = watchlist["ChangePercent"].apply(format_change)

    styled_watchlist = watchlist.style.format({
        "OpenPrice": "R{:,.2f}",
        "HighPrice": "R{:,.2f}",
        "LowPrice": "R{:,.2f}",
        "ClosePrice": "R{:,.2f}",
        "Volume": "{:,.0f}",
        "High52Week": "R{:,.2f}",
        "Low52Week": "R{:,.2f}"
    }).map(
        lambda value: "color: green; font-weight: bold;",
        subset=["HighPrice", "High52Week"]
    ).map(
        lambda value: "color: red; font-weight: bold;",
        subset=["LowPrice", "Low52Week"]
    ).map(
        style_change,
        subset=["ChangePercent"]
    )

    st.dataframe(
        styled_watchlist,
        use_container_width=True
    )


with tab3:
    st.subheader(
        f"Stock Analysis: {selected_ticker}"
    )

    if not selected_df.empty:
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=selected_df["Date"],
            open=selected_df["OpenPrice"],
            high=selected_df["HighPrice"],
            low=selected_df["LowPrice"],
            close=selected_df["ClosePrice"],
            name="OHLC"
        ))

        fig.update_layout(
            title=f"{selected_ticker} Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        latest = selected_df.iloc[-1]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Close Price",
            f"R{latest['ClosePrice']:,.2f}"
        )

        c2.metric(
            "High Price",
            f"R{latest['HighPrice']:,.2f}"
        )

        c3.metric(
            "Low Price",
            f"R{latest['LowPrice']:,.2f}"
        )

        c4.metric(
            "Volume",
            f"{latest['Volume']:,.0f}"
        )

    else:
        st.warning("No stock data found.")


with tab4:
    st.subheader(
        f"Technical Indicators: {selected_ticker}"
    )

    if not selected_df.empty:
        fig_ma = go.Figure()

        fig_ma.add_trace(go.Scatter(
            x=selected_df["Date"],
            y=selected_df["ClosePrice"],
            name="Close Price"
        ))

        fig_ma.add_trace(go.Scatter(
            x=selected_df["Date"],
            y=selected_df["SMA20"],
            name="SMA 20"
        ))

        fig_ma.add_trace(go.Scatter(
            x=selected_df["Date"],
            y=selected_df["SMA50"],
            name="SMA 50"
        ))

        fig_ma.update_layout(
            title="Moving Averages",
            xaxis_title="Date",
            yaxis_title="Price",
            height=400
        )

        st.plotly_chart(
            fig_ma,
            use_container_width=True
        )

        fig_rsi = go.Figure()

        fig_rsi.add_trace(go.Scatter(
            x=selected_df["Date"],
            y=selected_df["RSI14"],
            name="RSI 14"
        ))

        fig_rsi.add_hline(
            y=70,
            line_dash="dash"
        )

        fig_rsi.add_hline(
            y=30,
            line_dash="dash"
        )

        fig_rsi.update_layout(
            title="RSI Indicator",
            height=350
        )

        st.plotly_chart(
            fig_rsi,
            use_container_width=True
        )

        fig_macd = go.Figure()

        fig_macd.add_trace(go.Scatter(
            x=selected_df["Date"],
            y=selected_df["MACDLine"],
            name="MACD Line"
        ))

        fig_macd.add_trace(go.Scatter(
            x=selected_df["Date"],
            y=selected_df["MACDSignal"],
            name="Signal Line"
        ))

        fig_macd.add_trace(go.Bar(
            x=selected_df["Date"],
            y=selected_df["MACDHistogram"],
            name="Histogram"
        ))

        fig_macd.update_layout(
            title="MACD Indicator",
            height=350
        )

        st.plotly_chart(
            fig_macd,
            use_container_width=True
        )

    else:
        st.warning("No indicators available.")


with tab5:
    st.subheader(
        "Moving Average Trading Signals"
    )

    if not signals.empty:
        st.dataframe(
            signals,
            use_container_width=True
        )

        buy_count = len(
            signals[
                signals["Signal"].str.contains(
                    "BUY",
                    na=False
                )
            ]
        )

        sell_count = len(
            signals[
                signals["Signal"].str.contains(
                    "SELL",
                    na=False
                )
            ]
        )

        hold_count = len(
            signals[
                signals["Signal"].str.contains(
                    "HOLD",
                    na=False
                )
            ]
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Buy Signals",
            buy_count
        )

        c2.metric(
            "Sell Signals",
            sell_count
        )

        c3.metric(
            "Hold Signals",
            hold_count
        )

    else:
        st.info("No trading signals available.")


with tab6:
    st.subheader(
        f"{date_range} High/Low: {selected_ticker}"
    )

    if not selected_df.empty:
        high_value = selected_df["HighPrice"].max()
        low_value = selected_df["LowPrice"].min()

        c1, c2 = st.columns(2)

        c1.metric(
            f"{date_range} High",
            f"R{high_value:,.2f}"
        )

        c2.metric(
            f"{date_range} Low",
            f"R{low_value:,.2f}"
        )

        fig_range = go.Figure()

        fig_range.add_trace(go.Scatter(
            x=selected_df["Date"],
            y=selected_df["HighPrice"],
            name="High Price"
        ))

        fig_range.add_trace(go.Scatter(
            x=selected_df["Date"],
            y=selected_df["LowPrice"],
            name="Low Price"
        ))

        fig_range.update_layout(
            title=f"{selected_ticker} High vs Low",
            xaxis_title="Date",
            yaxis_title="Price",
            height=400
        )

        st.plotly_chart(
            fig_range,
            use_container_width=True
        )

        st.dataframe(
            selected_df[
                [
                    "Date",
                    "OpenPrice",
                    "HighPrice",
                    "LowPrice",
                    "ClosePrice",
                    "Volume"
                ]
            ],
            use_container_width=True
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
    unsafe_allow_html=True
)

st.caption(
    f"Last refreshed: "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
