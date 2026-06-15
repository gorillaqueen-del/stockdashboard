# Save this file exactly as global_stock_dashboard.py
# Execute via terminal interface: streamlit run global_stock_dashboard.py
import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
# -----------------------------------------------------------------------------
# 1. Page Architectural Configuration & Custom Themes
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Global Equities Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
# Implementation of high-contrast professional dark-mode design system
st.markdown(
    """
    <style>
    .reportview-container {
        background: #0f172a;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
    }
    div[data-testid="stMetricDelta"] {
        font-weight: 600;
    }
    .status-box {
        padding: 20px;
        border-radius: 8px;
        background-color: #1e293b;
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)
# -----------------------------------------------------------------------------
# 2. Hardcoded Cross-Border Asset Ecosystem Data Structure
# -----------------------------------------------------------------------------
# Contains correct market suffixes crucial for real-time international resolution
GLOBAL_MARKET_REGISTRY = {
    "United States (US)": {
        "index_ticker": "^GSPC",  # S&P 500 Index
        "index_name": "S&P 500 Index",
        "currency": "USD",
        "macro_outlook": "High premium structural positioning driven by AI infrastructure capitalization cycles.",
        "assets": {
            "NVIDIA Corporation": "NVDA",
            "Apple Inc.": "AAPL",
            "Microsoft Corporation": "MSFT",
            "Alphabet Inc.": "GOOGL",
            "Tesla Inc.": "TSLA",
        },
    },
    "Hong Kong (HK)": {
        "index_ticker": "^HSI",  # Hang Seng Index
        "index_name": "Hang Seng Index",
        "currency": "HKD",
        "macro_outlook": "Substantial valuation recovery supported by heavy Southbound Stock Connect liquidity inflows.",
        "assets": {
            "Tencent Holdings (0700)": "0700.HK",
            "Alibaba Group (9988)": "9988.HK",
            "Meituan (3690)": "3690.HK",
            "BYD Company (1211)": "1211.HK",
            "AIA Group (1299)": "1299.HK",
        },
    },
    "Mainland China (CN)": {
        "index_ticker": "000001.SS",  # SSE Composite Index
        "index_name": "Shanghai Composite",
        "currency": "CNY",
        "macro_outlook": "Structural rotation toward advanced industrial nodes and state-supported semiconductor self-reliance.",
        "assets": {
            "Kweichow Moutai (600519)": "600519.SS",
            "CATL (300750)": "300750.SZ",
            "Ping An Insurance (601318)": "601318.SS",
            "BYD Co. (002594)": "002594.SZ",
            "China Merchants Bank (600036)": "600036.SS",
        },
    },
}
# -----------------------------------------------------------------------------
# 3. Sidebar Control Panel Mechanics
# -----------------------------------------------------------------------------
st.sidebar.title("🌐 Global Selection Engine")
st.sidebar.markdown("---")
target_region = st.sidebar.selectbox(
    "Select Target Market:", list(GLOBAL_MARKET_REGISTRY.keys())
)
region_meta = GLOBAL_MARKET_REGISTRY[target_region]
asset_registry = region_meta["assets"]
target_asset_name = st.sidebar.selectbox(
    "Select Target Asset to Inspect:", list(asset_registry.keys())
)
target_ticker = asset_registry[target_asset_name]
st.sidebar.markdown("### 🗓️ Time Horizon Framework")
horizon_selection = st.sidebar.radio(
    "Select Time window:",
    options=["1 Month", "6 Months", "1 Year", "5 Years"],
    index=2,
)
# Convert human horizons into concrete chronological dates
current_date = datetime.date.today()
if horizon_selection == "1 Month":
    historical_start = current_date - datetime.timedelta(days=30)
elif horizon_selection == "6 Months":
    historical_start = current_date - datetime.timedelta(days=182)
elif horizon_selection == "1 Year":
    historical_start = current_date - datetime.timedelta(days=365)
else:
    historical_start = current_date - datetime.timedelta(days=365 * 5)
# -----------------------------------------------------------------------------
# 4. Data Fetching & Caching Layer
# -----------------------------------------------------------------------------
@st.cache_data(ttl=600)  # Caches results for 10 minutes to minimize API throttling
def pull_market_data(ticker_string, start_pt, end_pt):
    try:
        ticker_object = yf.Ticker(ticker_string)
        historical_dataframe = ticker_object.history(start=start_pt, end=end_pt)
        metadata_dictionary = ticker_object.info
        return historical_dataframe, metadata_dictionary
    except Exception as network_error:
        return pd.DataFrame(), {"error": str(network_error)}
# Execute parallel tracking pipelines for regional benchmark and targeted asset
index_df, index_metadata = pull_market_data(
    region_meta["index_ticker"], historical_start, current_date
)
asset_df, asset_metadata = pull_market_data(
    target_ticker, historical_start, current_date
)
# -----------------------------------------------------------------------------
# 5. Core Interface Construction (Tabs Layout Architecture)
# -----------------------------------------------------------------------------
st.title("📈 Multi-Market Strategy & Recommendation Dashboard")
st.markdown(
    f"Analyzing sovereign data systems for **{target_region}** market sectors."
)
tab_overview, tab_analysis = st.tabs(
    ["🌍 Regional Macro View", "🔍 Deep Asset Analysis"]
)
# --- TAB 1: REGIONAL MACRO VIEW ---
with tab_overview:
    st.subheader(f"Macro Landscape Summary: {region_meta['index_name']}")
    # Render regional structural briefing statement
    st.markdown(
        f"""
        <div class="status-box">
            <strong>Institutional Market Outlook:</strong> {region_meta['macro_outlook']}
        </div>
    """,
        unsafe_allow_html=True,
    )
    # Compute high-level index changes
    if not index_df.empty and len(index_df) >= 2:
        latest_index_close = index_df["Close"].iloc[-1]
        previous_index_close = index_df["Close"].iloc[-2]
        index_percentage_delta = (
            (latest_index_close - previous_index_close) / previous_index_close
        ) * 100
        col_idx1, col_idx2 = st.columns(2)
        with col_idx1:
            st.metric(
                label=f"Current {region_meta['index_name']} Closing Level",
                value=f"{latest_index_close:,.2f}",
                delta=f"{index_percentage_delta:+.2f}% (Daily Change)",
            )
        with col_idx2:
            st.metric(
                label="Base Trading Currency", value=region_meta["currency"]
            )
        # Plot Index Historical Performance
        fig_idx = go.Figure()
        fig_idx.add_trace(
            go.Scatter(
                x=index_df.index,
                y=index_df["Close"],
                mode="lines",
                name=region_meta["index_name"],
                line=dict(color="#3b82f6", width=2),
            )
        )
        fig_idx.update_layout(
            template="plotly_dark",
            title=f"{region_meta['index_name']} Trend Over Selected Horizon",
            xaxis_title="Date Timeline",
            yaxis_title="Index Points",
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_idx, use_container_width=True)
    else:
        st.warning("Regional macroeconomic benchmark index stream temporarily unavailable.")
# --- TAB 2: DEEP ASSET ANALYSIS ---
with tab_analysis:
    if not asset_df.empty and len(asset_df) >= 2:
        latest_asset_close = asset_df["Close"].iloc[-1]
        previous_asset_close = asset_df["Close"].iloc[-2]
        asset_percentage_delta = (
            (latest_asset_close - previous_asset_close) / previous_asset_close
        ) * 100
        # Row 1: KPI Statistics Overview Cards
        col_ast1, col_ast2, col_ast3 = st.columns(3)
        with col_ast1:
            st.metric(
                label=f"{target_asset_name} Close Value",
                value=f"{latest_asset_close:,.2f} {region_meta['currency']}",
                delta=f"{asset_percentage_delta:+.2f}% (Daily)",
            )
        with col_ast2:
            pe_multiple = asset_metadata.get("trailingPE", "N/A")
            if isinstance(pe_multiple, (int, float)):
                pe_display = f"{pe_multiple:.2f}x"
            else:
                pe_display = "N/A"
            st.metric(label="Trailing P/E Valuation Multiple", value=pe_display)
        with col_ast3:
            market_cap_value = asset_metadata.get("marketCap", "N/A")
            if isinstance(market_cap_value, (int, float)):
                market_cap_display = f"${market_cap_value:,.0f}"
            else:
                market_cap_display = "N/A"
            st.metric(label="Total Market Capitalization", value=market_cap_display)
        st.markdown("---")
        # Row 2: Interactive Candlestick Charting vs Fundamentals
        layout_col_left, layout_col_right = st.columns([2, 1])
        with layout_col_left:
            st.subheader("📊 Interactive Candlestick Pricing Stream")
            fig_candlestick = go.Figure()
            fig_candlestick.add_trace(
                go.Candlestick(
                    x=asset_df.index,
                    open=asset_df["Open"],
                    high=asset_df["High"],
                    low=asset_df["Low"],
                    close=asset_df["Close"],
                    name="Intraday Range History",
                )
            )
            fig_candlestick.update_layout(
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                margin=dict(l=20, r=20, t=10, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_candlestick, use_container_width=True)
        with layout_col_right:
            st.subheader("📋 Corporate Structural Profile")
            # Extract data layers while ensuring reliable cross-border fallbacks
            high_52w = asset_metadata.get("fiftyTwoWeekHigh", "N/A")
            low_52w = asset_metadata.get("fiftyTwoWeekLow", "N/A")
            div_yield_raw = asset_metadata.get("dividendYield", 0)
            div_yield_display = (
                f"{div_yield_raw * 100:.2f}%"
                if isinstance(div_yield_raw, (int, float))
                else "0.00%"
            )
            st.markdown(
                f"""
                | Fundamental Metric Ledger | Current Parameter Value |
                | :--- | :--- |
                | **System Symbol Ticker** | `{target_ticker}` |
                | **52-Week Peak Value Range** | {high_52w} |
                | **52-Week Trough Value Range** | {low_52w} |
                | **Annualized Dividend Yield** | {div_yield_display} |
            """
            )
            # Algorithmic Strategic Signal Engine Logic Block
            st.subheader("💡 System Trade Signal Guidance")
            if isinstance(pe_multiple, (int, float)):
                if pe_multiple < 16:
                    st.success(
                        "🟢 **Deep Value/Accumulation Play:** Asset trades below regional premium baselines. High structural margin of safety."
                    )
                elif 16 <= pe_multiple <= 35:
                    st.warning(
                        "🟡 **Fair Value / Consolidation Play:** Core multi-factor pricing is within standard historical standard deviations."
                    )
                else:
                    st.error(
                        "🔴 **Premium Growth Play:** High valuation multiplier present. Momentum validation and clear earnings expansion required."
                    )
            else:
                st.info(
                    "🔵 **Data Update Pending:** Direct trailing multi-variable valuation data points are missing for this specific international asset node."
                )
    else:
        st.error(
            "Target financial data stream unresolved. Verify data routing or corporate exchange suffix structures."
        )
