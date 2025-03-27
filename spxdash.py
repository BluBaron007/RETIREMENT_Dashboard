import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="SPX ➝ SPY Dashboard", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'SF Pro Display', sans-serif;
        background-color: #CD5C5C;
        color: #1c1c1e;
    }
    .stApp {
        background-color: #CD5C5C;
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

st.title("📊 SPX ➝ SPY Estimator Dashboard")

# Estimate function
def estimate_spy(spx_val):
    return round(spx_val / 10, 2)

# --- Tracking Error Visualization with Comparison ---
st.subheader("📈 SPY Comparison Chart")
compare_ticker = st.text_input("Please choose a stock (e.g. AAPL, MSFT, TSLA):", value="AAPL")

try:
    spy_hist = yf.download("SPY", period="1y")
    spx_hist = yf.download("^GSPC", period="1y")
    custom_hist = yf.download(compare_ticker.upper(), period="1y")

    spy_hist = spy_hist[['Close']].rename(columns={'Close': 'SPY_Actual'})
    spx_hist = spx_hist[['Close']].rename(columns={'Close': 'SPX'})
    custom_hist = custom_hist[['Close']].rename(columns={'Close': compare_ticker.upper()})

    combined = spy_hist.join(spx_hist, how='inner')
    combined['SPY_Estimated'] = combined['SPX'] / 10
    combined = combined.join(custom_hist, how='inner')

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(combined.index, combined['SPY_Actual'], label='SPY Actual', linewidth=2, color='#483D8B')
    ax.plot(combined.index, combined['SPY_Estimated'], '--', label='SPY Estimated (SPX/10)', linewidth=2, color='#6A5ACD')
    ax.plot(combined.index, combined[compare_ticker.upper()], label=compare_ticker.upper(), linewidth=2, color='#9370DB')
    ax.set_title(f"SPY vs Estimated SPY vs {compare_ticker.upper()}", fontsize=14, color='#483D8B')
    ax.set_ylabel("Price", fontsize=12)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)
except Exception as e:
    st.error("Failed to load historical data. Check your internet connection or ticker symbol.")

# --- Sensitivity Table ---
st.subheader("🧮 Sensitivity Table")
spx_range = np.arange(5400, 6001, 25)
sensitivity_df = pd.DataFrame({
    'SPX': spx_range,
    'Estimated SPY': [estimate_spy(spx) for spx in spx_range]
})
st.dataframe(sensitivity_df.style.format({"SPX": "{:.2f}", "Estimated SPY": "{:.2f}"}), use_container_width=True)

# --- Manual Estimator ---
st.subheader("✍️ Manual SPX Entry")
user_spx = st.number_input("Enter SPX Value", min_value=0.0, value=5500.0, step=1.0)
spy_estimate = estimate_spy(user_spx)
st.metric(label="Estimated SPY", value=f"${spy_estimate:.2f}")

st.caption("✨ https://github.com/BluBaron007?tab=repositories")
