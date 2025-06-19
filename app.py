"""
Streamlit App Interface
Author: Avory Campbell
Columbia University, Department of Computer Science

Provides an interactive front-end to analyze causality relationships between tickers using a browser-based UI.
"""

import streamlit as st
from utils import fetch_data
from visualize import plot_causality_heatmap
from causality_engine import run_granger

st.title("Market Signal Causality Analyzer")
st.markdown("Select assets to evaluate directional predictability using Granger causality.")

ticker_1 = st.text_input("Enter predictor ticker (e.g., AAPL)", value="AAPL")
ticker_2 = st.text_input("Enter response ticker (e.g., SPY)", value="SPY")
start_date = st.date_input("Start date")
end_date = st.date_input("End date")
max_lag = st.slider("Max lag (days)", 1, 10, 5)

if st.button("Run Causality Analysis"):
    try:
        df1 = fetch_data(ticker_1, start=start_date, end=end_date)
        df2 = fetch_data(ticker_2, start=start_date, end=end_date)

        # Make sure 'Close' column exists
        if 'Close' not in df1.columns or 'Close' not in df2.columns:
            st.error("Missing 'Close' column in one or both tickers.")
        else:
            p_values = run_granger(df1['Close'], df2['Close'], max_lag)
            st.success("Analysis complete. Plotting results...")
            plot_causality_heatmap(p_values, title=f"{ticker_1} → {ticker_2}", use_streamlit=True)
    except Exception as e:
        st.error(f"Error: {e}")

