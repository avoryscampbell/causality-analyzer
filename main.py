"""
Market Signal Causality Analyzer — Main Driver
Author: Avory Campbell
Columbia University, Department of Computer Science

Coordinates financial time series selection, causality testing, and visualization. User-facing entry point.
"""

from utils import fetch_data
from causality_engine import run_granger
from visualize import plot_causality_matrix

def main():
    tickers = ['AAPL', 'GOOGL', 'MSFT', 'META']
    target = 'SPY'
    start = '2020-01-01'
    end = '2024-01-01'
    max_lag = 5

    results = {}

    for ticker in tickers:
        print(f"Testing {ticker} → {target}")
        series_x = fetch_data(ticker, start, end)
        series_y = fetch_data(target, start, end)

        if len(series_x) != len(series_y):
            min_len = min(len(series_x), len(series_y))
            series_x = series_x[-min_len:]
            series_y = series_y[-min_len:]

        p_vals = run_granger(series_x, series_y, max_lag)
        results[ticker] = p_vals

    plot_causality_matrix(results, target)

if __name__ == "__main__":
    main()

