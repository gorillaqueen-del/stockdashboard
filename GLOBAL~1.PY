# global_stock_dashboard.py
# Run with: streamlit run global_stock_dashboard.py

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# -----------------------------------------------------------------------------
# Page Config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Buy Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
div[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
div[data-testid="stMetricLabel"] { font-size: 0.8rem; opacity: 0.75; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Stock Universe — US, Hong Kong, China
# -----------------------------------------------------------------------------
UNIVERSE = {
    "🇺🇸 United States": {
        "currency": "USD",
        "stocks": {
            "Apple":             "AAPL",
            "Microsoft":         "MSFT",
            "Alphabet":          "GOOGL",
            "Amazon":            "AMZN",
            "Meta":              "META",
            "NVIDIA":            "NVDA",
            "Tesla":             "TSLA",
            "JPMorgan":          "JPM",
            "Visa":              "V",
            "Johnson & Johnson": "JNJ",
            "Walmart":           "WMT",
            "Procter & Gamble":  "PG",
            "UnitedHealth":      "UNH",
            "Netflix":           "NFLX",
            "AMD":               "AMD",
            "Bank of America":   "BAC",
            "ExxonMobil":        "XOM",
            "Coca-Cola":         "KO",
            "Mastercard":        "MA",
            "Home Depot":        "HD",
        },
    },
    "🇭🇰 Hong Kong": {
        "currency": "HKD",
        "stocks": {
            "Tencent":      "0700.HK",
            "Alibaba":      "9988.HK",
            "Meituan":      "3690.HK",
            "BYD (HK)":    "1211.HK",
            "AIA Group":   "1299.HK",
            "HSBC":        "0005.HK",
            "China Mobile": "0941.HK",
            "HKEX":        "0388.HK",
            "Xiaomi":      "1810.HK",
            "Li Ning":     "2331.HK",
        },
    },
    "🇨🇳 Mainland China": {
        "currency": "CNY",
        "stocks": {
            "Kweichow Moutai":    "600519.SS",
            "CATL":               "300750.SZ",
            "Ping An Insurance":  "601318.SS",
            "BYD (CN)":           "002594.SZ",
            "China Merchants Bank": "600036.SS",
            "Wuliangye":          "000858.SZ",
            "Yangtze Power":      "600900.SS",
            "Midea Group":        "000333.SZ",
            "Industrial Bank":    "601166.SS",
            "Longi Green Energy": "601012.SS",
        },
    },
}

# -----------------------------------------------------------------------------
# Data Fetching (cached 1 hour)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock(ticker):
    try:
        obj = yf.Ticker(ticker)
        hist = obj.history(period="3mo")
        info = obj.info
        return hist, info
    except Exception:
        return pd.DataFrame(), {}

def get_momentum(hist):
    if hist.empty or len(hist) < 5:
        return None
    return ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100

def get_last_price(hist):
    if hist.empty:
        return None
    return hist["Close"].iloc[-1]

# -----------------------------------------------------------------------------
# Sidebar Filters
# -----------------------------------------------------------------------------
st.sidebar.title("🔍 Filters")
market_filter = st.sidebar.multiselect(
    "Markets", options=list(UNIVERSE.keys()), default=list(UNIVERSE.keys())
)
signal_filter = st.sidebar.multiselect(
    "Signal", options=["🟢 Strong Buy", "🟡 Buy", "🔵 Watch"],
    default=["🟢 Strong Buy", "🟡 Buy"]
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Scoring method**\n\n"
    "Each stock is ranked on:\n"
    "- 📈 **Momentum** — 3-month price return\n"
    "- 💰 **Value** — lower P/E = better\n\n"
    "Combined score out of 100."
)

# -----------------------------------------------------------------------------
# Load & Score All Stocks
# -----------------------------------------------------------------------------
st.title("🎯 Stock Buy Screener")
st.caption("Screens US, Hong Kong & China markets for value + momentum opportunities.")

progress = st.progress(0, text="Scanning markets...")
rows = []
all_tickers = [
    (market, name, ticker)
    for market, meta in UNIVERSE.items()
    for name, ticker in meta["stocks"].items()
]

for i, (market, name, ticker) in enumerate(all_tickers):
    progress.progress((i + 1) / len(all_tickers), text=f"Fetching {name}...")
    hist, info = fetch_stock(ticker)
    momentum = get_momentum(hist)
    price = get_last_price(hist)
    pe = info.get("trailingPE")
    high_52w = info.get("fiftyTwoWeekHigh")
    low_52w = info.get("fiftyTwoWeekLow")
    currency = UNIVERSE[market]["currency"]

    rows.append({
        "Market":        market,
        "Stock":         name,
        "Ticker":        ticker,
        "Currency":      currency,
        "Price":         price,
        "Momentum (3M)": momentum,
        "P/E Ratio":     pe if isinstance(pe, (int, float)) and 0 < pe < 200 else None,
        "52W High":      high_52w,
        "52W Low":       low_52w,
    })

progress.empty()

df = pd.DataFrame(rows)

# Percentile-rank momentum (higher = better)
df["Mom_Score"] = df["Momentum (3M)"].rank(pct=True) * 100

# Percentile-rank value: higher 1/PE = cheaper stock = better
df["PE_inv"] = df["P/E Ratio"].apply(lambda x: 1 / x if pd.notna(x) else None)
df["Val_Score"] = df["PE_inv"].rank(pct=True) * 100

# Combined score: average of whichever scores exist
def combined_score(row):
    scores = [s for s in [row["Mom_Score"], row["Val_Score"]] if pd.notna(s)]
    return round(sum(scores) / len(scores), 1) if scores else None

df["Score"] = df.apply(combined_score, axis=1)

def signal_label(score):
    if score is None:
        return "🔵 Watch"
    if score >= 70:
        return "🟢 Strong Buy"
    if score >= 50:
        return "🟡 Buy"
    return "🔵 Watch"

df["Signal"] = df["Score"].apply(signal_label)
df_sorted = df.sort_values("Score", ascending=False).reset_index(drop=True)

# Apply sidebar filters
filtered = df_sorted[
    df_sorted["Market"].isin(market_filter) &
    df_sorted["Signal"].isin(signal_filter)
]

# -----------------------------------------------------------------------------
# Top Picks — Metric Cards
# -----------------------------------------------------------------------------
st.subheader("🏆 Top Buy Picks")

top10 = filtered[filtered["Signal"].isin(["🟢 Strong Buy", "🟡 Buy"])].head(10)

if top10.empty:
    st.info("No stocks match the current filters.")
else:
    cols = st.columns(5)
    for i, (_, row) in enumerate(top10.iterrows()):
        with cols[i % 5]:
            price_str = f"{row['Price']:,.2f} {row['Currency']}" if row["Price"] else "N/A"
            mom_str = f"{row['Momentum (3M)']:+.1f}% (3M)" if pd.notna(row["Momentum (3M)"]) else "N/A"
            st.metric(
                label=f"{row['Signal']}  {row['Stock']}",
                value=price_str,
                delta=mom_str,
            )

st.markdown("---")

# -----------------------------------------------------------------------------
# Full Screener Table
# -----------------------------------------------------------------------------
st.subheader("📋 All Screened Stocks")

display = filtered[[
    "Signal", "Market", "Stock", "Ticker", "Price", "Currency",
    "Momentum (3M)", "P/E Ratio", "Score"
]].copy()

display["Price"] = display.apply(
    lambda r: f"{r['Price']:,.2f} {r['Currency']}" if pd.notna(r["Price"]) else "N/A", axis=1
)
display["Momentum (3M)"] = display["Momentum (3M)"].apply(
    lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A"
)
display["P/E Ratio"] = display["P/E Ratio"].apply(
    lambda x: f"{x:.1f}x" if pd.notna(x) else "N/A"
)
display["Score"] = display["Score"].apply(
    lambda x: f"{x:.0f} / 100" if pd.notna(x) else "N/A"
)
display = display.drop(columns=["Currency"])

st.dataframe(display, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# Stock Detail View
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🔍 Stock Detail")

stock_options = filtered["Stock"].tolist()
if stock_options:
    selected_name = st.selectbox("Select a stock to inspect:", stock_options)
    sel = filtered[filtered["Stock"] == selected_name].iloc[0]
    hist, info = fetch_stock(sel["Ticker"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Signal", sel["Signal"])
    with c2:
        st.metric("Score", f"{sel['Score']:.0f} / 100" if pd.notna(sel["Score"]) else "N/A")
    with c3:
        st.metric("3M Momentum", f"{sel['Momentum (3M)']:+.1f}%" if pd.notna(sel["Momentum (3M)"]) else "N/A")
    with c4:
        st.metric("P/E Ratio", f"{sel['P/E Ratio']:.1f}x" if pd.notna(sel["P/E Ratio"]) else "N/A")

    if not hist.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist["Close"],
            mode="lines",
            fill="tozeroy",
            line=dict(color="#3b82f6", width=2),
            fillcolor="rgba(59,130,246,0.1)",
            name="Close Price",
        ))
        # Highlight last price
        fig.add_hline(
            y=hist["Close"].iloc[-1],
            line_dash="dot",
            line_color="#f59e0b",
            annotation_text=f"Last: {hist['Close'].iloc[-1]:,.2f}",
            annotation_position="bottom right",
        )
        fig.update_layout(
            template="plotly_dark",
            title=f"{selected_name} ({sel['Ticker']}) — 3 Month Price Chart",
            xaxis_title="Date",
            yaxis_title=f"Price ({sel['Currency']})",
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

        # 52-week range bar
        high_52 = sel["52W High"]
        low_52 = sel["52W Low"]
        last_price = sel["Price"]
        if all(pd.notna(v) for v in [high_52, low_52, last_price]):
            pct_in_range = (last_price - low_52) / (high_52 - low_52) * 100
            st.markdown(f"**52-Week Range:** {low_52:,.2f} ↔ {high_52:,.2f} &nbsp;|&nbsp; Currently at **{pct_in_range:.0f}%** of range")
            st.progress(int(min(max(pct_in_range, 0), 100)))
else:
    st.info("No stocks match current filters.")

st.markdown("---")
st.caption("⚠️ For informational purposes only. Not financial advice. Always do your own research before investing.")
