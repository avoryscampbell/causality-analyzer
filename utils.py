"""
Financial Data Utilities
Author: Avory Campbell
Columbia University, Department of Computer Science

Fetches and processes historical price data using the Yahoo Finance API via yfinance.
"""

import yfinance as yf
import pandas as pd

def fetch_data(ticker, start=None, end=None):
    """
    Fetch historical price data for a given ticker using yfinance.

    Parameters:
        ticker (str): Ticker symbol (e.g., 'AAPL')
        start (str or datetime): Start date
        end (str or datetime): End date

    Returns:
        pd.DataFrame: DataFrame with historical prices
    """
    df = yf.download(ticker, start=start, end=end)
    return df

