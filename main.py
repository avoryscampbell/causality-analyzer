"""
Market Signal Causality Analyzer — Runner (top-level)
Author: Avory Campbell
"""

import sys
from typing import Dict

# Absolute imports from the backend package
from backend.utils import fetch_data
from backend.causality_engine import run_granger


try:
    from backend.visualize import plot_pvalues_by_lag
    HAVE_PLOTTER = True
except Exception:
    HAVE_PLOTTER = False


def analyze_pair(ticker_x: str, ticker_y: str, start: str, end: str, max_lag: int = 5) -> None:
    """
    Fetch, align by date, run Granger, and (optionally) plot.
    Expects run_granger(...) to return:
      { "p_values_by_lag": {1: p1, 2: p2, ...}, "best_lag": int, "min_p": float }
    """
    # 1) Load & align on dates
    df_x = fetch_data(ticker_x, start=start, end=end)[["Close"]].rename(columns={"Close": "x"})
    df_y = fetch_data(ticker_y, start=start, end=end)[["Close"]].rename(columns={"Close": "y"})
    df = df_x.join(df_y, how="inner").dropna()
    if df.empty:
        raise ValueError(f"No overlapping data for {ticker_x} and {ticker_y} in {start}..{end}")

    # 2) Run Granger
    result: Dict = run_granger(df["x"], df["y"], max_lag=max_lag)

    # 3)
    print(f"\n=== {ticker_x} → {ticker_y} (max_lag={max_lag}) ===")
    pmap = result.get("p_values_by_lag", {})
    if pmap:
        for lag in sorted(pmap):
            print(f"lag {lag}: p = {pmap[lag]:.5f}")
    if "best_lag" in result and "min_p" in result:
        print(f"best_lag: {result['best_lag']}, min_p: {result['min_p']:.5f}")

    # 4) Optional plot
    if HAVE_PLOTTER:
        try:
            plot_pvalues_by_lag(result, title=f"{ticker_x} → {ticker_y}")
        except Exception as e:
            print(f"[plot skipped] {e}")


def main() -> None:
    # ---- Config (edit these as you like) ----
    tickers = ["AAPL", "GOOGL", "MSFT", "META"]
    target = "SPY"
    start = "2020-01-01"
    end = "2024-01-01"
    max_lag = 5
    # -----------------------------------------

    print("Running Market Signal Causality Analyzer runner…")
    print(f"Python: {sys.version.split()[0]}  Dates: {start}..{end}")

    for t in tickers:
        analyze_pair(t, target, start, end, max_lag=max_lag)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")

