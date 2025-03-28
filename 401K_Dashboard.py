import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Vanguard Retirement Dashboard", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;600&display=swap');

    html, body, [class*="css"]  {
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

# Vanguard retirement fund tickers
vanguard_funds = {
    "2025 - VTTVX": "VTTVX",
    "2030 - VTHRX": "VTHRX",
    "2040 - VFORX": "VFORX",
    "2050 - VFIFX": "VFIFX",
    "2060 - VTTSX": "VTTSX",
    "2070 - VSVNX": "VSVNX"
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
    data = yf.download(tickers, period="5y")['Adj Close']

    st.subheader("📈 5-Year Performance Chart with Moving Averages")
    fig, ax = plt.subplots(figsize=(10, 5))
    for ticker in tickers:
        normalized = data[ticker] / data[ticker].iloc[0] * 100
        ax.plot(normalized, label=f"{ticker} (Price)", linewidth=2)
        for ma in ma_options:
            ma_series = data[ticker].rolling(window=ma).mean()
            ma_normalized = ma_series / data[ticker].iloc[0] * 100
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

st.divider()

st.page_link("pages/SPX_SPY_Estimator.py", label="📉 Go to SPX ➝ SPY Estimator", icon="📊")
