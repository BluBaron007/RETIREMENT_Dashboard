import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Vanguard Retirement Dashboard", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'SF Pro Display', sans-serif;
        background-color: #F8F8FF;
        color: #1c1c1e;
    }
    .stApp {
        background-color: #F8F8FF;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, .stMetricLabel, .stMarkdown {
        color: #483D8B;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Vanguard Retirement Fund Dashboard")

vanguard_funds = {
    "2025 - VTTVX": "VTTVX",
    "2030 - VTHRX": "VTHRX",
    "2040 - VFORX": "VFORX",
    "2050 - VFIFX": "VFIFX",
    "2060 - VTTSX": "VTTSX",
    "2070 - VSVNX": "VSVNX",
    "Vanguard Growth - VIGRX": "VIGRX"
}

selected_funds = st.multiselect(
    "Select Vanguard Retirement Funds to Compare:",
    options=list(vanguard_funds.keys()),
    default=["2040 - VFORX", "2050 - VFIFX"]
)

ma_options = st.multiselect(
    "Select Moving Averages to Display:",
    options=[10, 50, 75, 200],
    default=[10, 50, 200]
)

if selected_funds:
    tickers = [vanguard_funds[fund] for fund in selected_funds]
    raw_data = yf.download(tickers, period="5y", progress=False)
    if isinstance(raw_data.columns, pd.MultiIndex):
        data = raw_data['Adj Close']
    else:
        data = raw_data[['Adj Close']].rename(columns={'Adj Close': tickers[0]})

    st.subheader("📈 5-Year Performance Chart with Moving Averages")
    fig, ax = plt.subplots(figsize=(10, 5))

    for ticker in tickers:
        col_name = ticker if ticker in data.columns else data.columns[0]
        normalized = data[col_name] / data[col_name].iloc[0] * 100
        ax.plot(normalized, label=f"{ticker} (Price)", linewidth=2)
        for ma in ma_options:
            ma_series = data[col_name].rolling(window=ma).mean()
            ma_normalized = ma_series / data[col_name].iloc[0] * 100
            ax.plot(ma_normalized, linestyle='--', alpha=0.6, label=f"{ticker} {ma}-day MA")

    ax.set_title("Normalized Performance of Selected Vanguard Funds", fontsize=14, color="#483D8B")
    ax.set_ylabel("Growth (%)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc='upper left')
    st.pyplot(fig)

    st.subheader("📊 Fund Statistics")
    returns = data.pct_change().dropna()
    cagr = ((data.iloc[-1] / data.iloc[0]) ** (1 / 5) - 1)
    vol = returns.std()
    drawdown = (data / data.cummax() - 1).min()
    current_prices = data.iloc[-1]

    ma_comparisons = {
        f"MA {ma} Position": [
            "Above" if current_prices[ticker] > data[ticker].rolling(ma).mean().iloc[-1] else "Below"
            for ticker in tickers
        ] for ma in ma_options
    }

    stats = pd.DataFrame({
        "Current Price": current_prices,
        "CAGR": cagr.map(lambda x: f"{x:.2%}"),
        "Volatility (Std Dev)": vol.map(lambda x: f"{x:.2%}"),
        "Max Drawdown": drawdown.map(lambda x: f"{x:.2%}")
    })

    for ma, positions in ma_comparisons.items():
        stats[ma] = positions

    st.dataframe(stats)

    st.subheader("📅 Projected Value Calculator")
    col1, col2, col3 = st.columns(3)
    with col1:
        target_year = st.slider("Target Year", min_value=datetime.now().year+1, max_value=2075, value=2050)
    with col2:
        monthly_investment = st.number_input("Monthly Investment ($)", min_value=0, value=500, step=50)
    with col3:
        expected_return = st.slider("Expected Annual Return (%)", 1.0, 12.0, 6.0, step=0.1)

    current_year = datetime.now().year
    years = target_year - current_year
    r = expected_return / 100 / 12  # monthly rate
    n = 12 * years

    if r > 0:
        future_value = monthly_investment * (((1 + r) ** n - 1) / r)
    else:
        future_value = monthly_investment * n

    st.markdown(f"### 📈 Projected Value by {target_year}: **${future_value:,.2f}**")

    # Plot growth curve
    future_values = [monthly_investment * (((1 + r) ** (12 * yr) - 1) / r) if r > 0 else monthly_investment * 12 * yr for yr in range(1, years + 1)]
    future_df = pd.DataFrame({"Year": list(range(current_year + 1, target_year + 1)), "Projected Value": future_values})

    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(future_df["Year"], future_df["Projected Value"], color="#483D8B", linewidth=2)
    ax2.set_title("Projected Investment Growth Over Time")
    ax2.set_ylabel("Total Value ($)")
    ax2.set_xlabel("Year")
    ax2.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig2)

st.caption("📈 This dashboard tracks historical and technical data for major Vanguard retirement funds, with projections for future planning.")
