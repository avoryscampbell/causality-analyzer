"""
Causality Visualization Module
Author: Avory Campbell
Columbia University, Department of Computer Science

Generates annotated heatmaps that illustrate Granger p-values across lags and tickers.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def plot_causality_heatmap(p_values, title="Granger Causality Heatmap"):
    """
    Plot a simple heatmap of p-values for each lag.

    Parameters:
        p_values (dict): Dictionary of {lag: p-value}
        title (str): Title for the heatmap
    """
    lags = list(p_values.keys())
    values = list(p_values.values())

    fig, ax = plt.subplots()
    sns.heatmap(
        [values],
        annot=True,
        fmt=".3f",
        xticklabels=lags,
        yticklabels=["p-values"],
        cmap="coolwarm",
        cbar=True,
        ax=ax
    )
    ax.set_title(title)
    ax.set_xlabel("Lag")
    st.pyplot(fig)

