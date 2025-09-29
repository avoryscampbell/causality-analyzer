"""
Financial Data Utilities
Author: Avory Campbell

Robust helpers to fetch and clean historical price data with yfinance.
"""

from __future__ import annotations
from functools import lru_cache
from typing import Optional, List
import pandas as pd
import yfinance as yf
from functools import lru_cache
from typing import Optional

@lru_cache(maxsize=256)
def fetch_data(
    ticker: str,
    start: Optional[str] = None,   
    end: Optional[str] = None,
    interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical data for a single ticker and return a DataFrame
    with exactly one column named 'Close'. Uses Adjusted Close when available.
    """
    if not ticker or not isinstance(ticker, str):
        raise ValueError("ticker must be a non-empty string.")
        
    try:
        raw = yf.download(
            tickers=ticker,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=False,   # we'll choose the column explicitly
            progress=False,
            threads=True,     
        )
    except Exception as e:
        raise RuntimeError(f"yfinance download failed for {ticker}: {e}") from e
    
    # Clean & normalize (your _clean_prices should already pick Adj Close/Close)
    df = _clean_prices(raw)

    # Ensure a DataFrame with exactly one column named 'Close'
    if isinstance(df, pd.Series):
        df = df.to_frame(name="Close")
    else:
        # If more than one column slipped through, take the first
        if df.shape[1] > 1:
            first_col = df.columns[0]
            df = df.iloc[:, [0]].rename(columns={first_col: "Close"})
        else:
            # Exactly one column—rename if needed
            only_col = df.columns[0]
            if only_col != "Close":
                df = df.rename(columns={only_col: "Close"})
    
    if df.empty:
        raise ValueError(f"No price data returned for {ticker} in range {start}..{end}")
    return df


def _clean_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize a yfinance download into a DataFrame with a single 'Close' column,
    forward-fill gaps, drop remaining NaNs, and ensure a sorted DatetimeIndex.
    """
    if df is None or df.empty:
        raise ValueError("Empty dataframe from data source.")

    # yfinance single-ticker returns columns: ['Open','High','Low','Close','Adj Close','Volume']
    # multi-ticker returns MultiIndex columns: ('Adj Close','AAPL'), ...
    if isinstance(df.columns, pd.MultiIndex):
        # Prefer 'Adj Close' if present, else 'Close'
        top_levels = set(df.columns.get_level_values(0).unique())
        if "Adj Close" in top_levels:
            df = df["Adj Close"]
        elif "Close" in top_levels:
            df = df["Close"]
        else:
            raise ValueError("Expected 'Adj Close' or 'Close' in multi-ticker download.")
        # df columns are tickers now
    else:
        if "Adj Close" in df.columns:
            df = df[["Adj Close"]].rename(columns={"Adj Close": "Close"})
        elif "Close" in df.columns:
            df = df[["Close"]]
        else:
            raise ValueError("Expected 'Adj Close' or 'Close' in single-ticker download.")

    # Index hygiene
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors="coerce")

    df = df.sort_index()
    # Fill small gaps; safe for daily bars
    df = df.ffill().dropna()

    if df.empty:
        raise ValueError("No usable rows after cleaning/filling price data.")
    return df

@lru_cache(maxsize=64)
def fetch_many(
    tickers: tuple,
    start: Optional[str] = None,
    end: Optional[str] = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch and align multiple tickers into one DataFrame with columns named by ticker.
    Uses Adjusted Close when available, falls back to Close.
    """
    if not tickers or len(tickers) < 2:
        raise ValueError("Provide at least two tickers.")

    try:
        raw = yf.download(
            tickers=list(tickers),
            start=start,
            end=end,
            interval=interval,
            auto_adjust=False,
            progress=False,
            threads=True,
            group_by="column",
        )
    except Exception as e:
        raise RuntimeError(f"yfinance multi-download failed: {e}") from e

    df = _clean_prices(raw)

    # After _clean_prices on multi, columns should be tickers. Ensure all present.
    missing = [t for t in tickers if t not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for: {missing}")

    df = df[list(tickers)]
    return df

