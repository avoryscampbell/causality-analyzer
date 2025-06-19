"""
Granger Causality Testing Module
Author: Avory Campbell
Columbia University, Department of Computer Science

Implements lag-wise Granger causality tests with statistical significance outputs.
"""

import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests

def run_granger(series_x, series_y, max_lag=5):
    """
    Perform Granger causality test for whether series_x causes series_y.

    Parameters:
        series_x (pd.Series): Potential predictor time series
        series_y (pd.Series): Response time series
        max_lag (int): Maximum lag order to test

    Returns:
        dict: Dictionary mapping lag -> p-value
    """
    df = pd.concat([series_y, series_x], axis=1)
    df.columns = ['y', 'x']
    df.dropna(inplace=True)

    results = {}
    for lag in range(1, max_lag + 1):
        try:
            test_result = grangercausalitytests(df, maxlag=lag, verbose=False)
            p_val = test_result[lag][0]['ssr_ftest'][1]
            results[lag] = p_val
        except Exception as e:
            results[lag] = None
            print(f"Granger test failed for lag {lag}: {e}")
    return results


