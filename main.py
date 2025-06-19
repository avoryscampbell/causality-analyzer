"""
Market Signal Causality Analyzer — Entry Script
Author: Avory Campbell
Columbia University, Department of Computer Science

Orchestrates Granger causality analysis between selected market tickers and a target index.
"""

from utils import fetch_data
from causality_engine import run_granger
from visualize import plot_causality_heatmap

def main():
    # Configuration
    tickers = ['AAPL', 'GOOGL', 'MSFT', 'META']
    target = 'SPY'
    start = '2020-01-01'
    end = '2024-01-01'
    max_lag = 5

    for ticker in tickers:
        print(f"\nTesting {ticker} → {target}")
        df_x = fetch_data(ticker, start=start, end=end)
        df_y = fetch_data(target, start=start, end=end)

        # Ensure equal lengths
        min_len = min(len(df_x), len(df_y))
        series_x = df_x['Close'].tail(min_len)
        series_y = df_y['Close'].tail(min_len)

        # Run Granger causality test
        p_values = run_granger(series_x, series_y, max_lag=max_lag)

        # Visualize results
        plot_causality_heatmap(p_values, title=f"{ticker} → SPY", use_streamlit=False)

if __name__ == "__main__":
    main()

