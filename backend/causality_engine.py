# backend/causality_engine.py
from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests

# Optional: only import if you plan to use ticker-based helpers below
# (Comment out if you don't have backend/utils.py with fetch_data)
try:
    from .utils import fetch_data  # noqa: F401
    HAVE_FETCH = True
except Exception:
    HAVE_FETCH = False


def run_granger(series_x: pd.Series, series_y: pd.Series, max_lag: int = 5) -> Dict:
    """
    Does X Granger-cause Y?
    Parameters
    ----------
    series_x : pd.Series
        Candidate 'cause' (predictor) series.
    series_y : pd.Series
        Target (response) series.
    max_lag : int
        Maximum lag order to test (>=1).

    Returns
    -------
    dict
        {
          "p_values_by_lag": {1: p1, 2: p2, ...},
          "best_lag": <int>,        # lag with smallest p-value
          "min_p": <float>,         # that smallest p-value
        }
    """
    if not isinstance(series_x, pd.Series) or not isinstance(series_y, pd.Series):
        raise TypeError("run_granger expects pandas Series for series_x and series_y.")
    if max_lag < 1:
        raise ValueError("max_lag must be >= 1")

    # Align by timestamp and order columns as [y, x] for statsmodels (tests x -> y)
    df = pd.concat(
        [series_y.rename("y"), series_x.rename("x")],
        axis=1
    ).dropna()

    if df.empty or len(df) <= (max_lag + 1):
        raise ValueError("Insufficient overlapping data after alignment for Granger test.")

    # statsmodels grangercausalitytests expects a 2D array with columns [y, x]
    res = grangercausalitytests(df[["y", "x"]].values, maxlag=max_lag, verbose=False)

    # Extract SSR F-test p-values for each lag
    pvals_by_lag = {int(lag): float(r[0]["ssr_ftest"][1]) for lag, r in res.items()}

    best_lag = min(pvals_by_lag, key=pvals_by_lag.get)
    return {
        "p_values_by_lag": pvals_by_lag,
        "best_lag": int(best_lag),
        "min_p": float(pvals_by_lag[best_lag]),
    }


def run_granger_symmetric_matrix(
    prices: pd.DataFrame,
    max_lag: int = 5,
    alpha: float = 0.05
) -> Dict:
    """
    Compute a full NxN matrix of min p-values for 'j -> i' across all columns in `prices`.

    Parameters
    ----------
    prices : pd.DataFrame
        Columns are tickers (or series names); index is time.
    max_lag : int
        Maximum lag to test.
    alpha : float
        Significance threshold for boolean matrix.

    Returns
    -------
    dict
        {
          "tickers": [...],
          "max_lag": <int>,
          "alpha": <float>,
          "p_values": [[...], ...],     # NxN matrix of min p-values (1.0 on diagonal)
          "significant": [[...], ...],  # NxN boolean matrix (False on diagonal)
        }
    """
    if not isinstance(prices, pd.DataFrame) or prices.shape[1] < 2:
        raise ValueError("prices must be a DataFrame with at least 2 columns.")

    # Convert to returns to stabilize series (you can change to log returns if you prefer)
    returns = prices.pct_change().dropna()
    tickers = list(returns.columns)
    n = len(tickers)
    pmat = np.ones((n, n), dtype=float)

    for i, target in enumerate(tickers):
        for j, cause in enumerate(tickers):
            if i == j:
                pmat[i, j] = 1.0
                continue
            df = pd.concat(
                [returns[target].rename("y"), returns[cause].rename("x")],
                axis=1
            ).dropna()
            if len(df) <= (max_lag + 1):
                pmat[i, j] = 1.0
                continue
            try:
                res = grangercausalitytests(df[["y", "x"]].values, maxlag=max_lag, verbose=False)
                best_p = min(r[0]["ssr_ftest"][1] for _, r in res.items())
                pmat[i, j] = float(best_p)
            except Exception:
                pmat[i, j] = 1.0

    significant = (pmat < alpha).astype(bool)
    np.fill_diagonal(significant, False)

    return {
        "tickers": tickers,
        "max_lag": int(max_lag),
        "alpha": float(alpha),
        "p_values": pmat.tolist(),
        "significant": significant.tolist(),
    }


# ---------- Optional: ticker-based helpers (use fetch_data if available) ----------

def load_prices_for(
    tickers: List[str],
    start: str,
    end: str
) -> pd.DataFrame:
    """
    Convenience wrapper to build a multi-column prices DataFrame using fetch_data.
    Requires backend/utils.py to define fetch_data(ticker, start=..., end=...) -> DataFrame with 'Close'.
    """
    if not HAVE_FETCH:
        raise ImportError("fetch_data not available. Ensure backend/utils.py defines it.")

    dfs = []
    for t in tickers:
        df = fetch_data(t, start=start, end=end)
        if "Close" not in df.columns:
            raise ValueError(f"'Close' column missing for {t}")
        dfs.append(df[["Close"]].rename(columns={"Close": t}))

    # Inner-join on timestamp index to align all series
    prices = dfs[0]
    for d in dfs[1:]:
        prices = prices.join(d, how="inner")
    prices = prices.dropna()
    if prices.empty:
        raise ValueError("No overlapping data across requested tickers/date range.")
    return prices
