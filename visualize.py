"""
Causality Visualization Module
Author: Avory Campbell
Columbia University, Department of Computer Science

Generates annotated heatmaps that illustrate Granger p-values across lags and tickers.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_causality_heatmap(p_values, title="Granger Causality Heatmap", use_streamlit=False):
    """
    Plot a heatmap of p-values from Granger causality testing.

    Parameters:
        p_values (dict): Mapping of lag → p-value
        title (str): Plot title
        use_streamlit (bool): Use Streamlit display if True; otherwise use plt.show()
    """
    lags = list(p_values.keys())
    values = list(p_values.values())

    fig, ax = plt.subplots()
    sns.heatmap(
        np.array([values]),
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

    if use_streamlit:
        import streamlit as st
        st.pyplot(fig)
    else:
        plt.tight_layout()
        plt.show()

