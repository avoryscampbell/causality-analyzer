"""
Causality Visualization Module
Author: Avory Campbell
Columbia University, Department of Computer Science

Generates annotated heatmaps that illustrate Granger p-values across lags and tickers.
"""

# backend/visualize.py
from __future__ import annotations
from typing import Dict, Optional
import matplotlib.pyplot as plt

def plot_pvalues_by_lag(result: Dict, title: Optional[str] = None):
    """
    Plot a simple bar chart of p-values by lag.
    Expects result = {"p_values_by_lag": {1: p1, 2: p2, ...}, "best_lag": int, "min_p": float}
    """
    pmap = result.get("p_values_by_lag", {})
    if not pmap:
        print("[plot] No p-values found in result.")
        return

    lags = sorted(pmap.keys())
    vals = [pmap[k] for k in lags]

    plt.figure(figsize=(6, 4))
    plt.bar([str(l) for l in lags], vals)
    plt.axhline(0.05, linestyle="--", linewidth=1)  # alpha reference
    plt.xlabel("Lag")
    plt.ylabel("p-value (SSR F-test)")
    plt.title(title or "Granger Causality — p-values by lag")
    plt.tight_layout()
    plt.show()

