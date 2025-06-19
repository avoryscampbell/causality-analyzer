# Market Signal Causality Analyzer

**Author:** Avory Campbell
**Columbia University, Department of Computer Science**

A professional-grade Python platform for analyzing Granger causality relationships between financial time series. Designed for quantitative signal discovery, market prediction, and time-series experimentation, this tool enables users to assess directional predictive power among equities, indices, or other assets using robust statistical tests and heatmap visualizations.

---

## Project Structure

```
causality-analyzer/
├── main.py               # CLI entry point: runs ticker selection, analysis, and plotting
├── utils.py              # Downloads and processes financial data from Yahoo Finance
├── causality_engine.py   # Performs Granger Causality tests using statsmodels
├── visualize.py          # Generates heatmaps of lag-wise causality significance
├── requirements.txt      # Dependency list for pip install
└── README.md             # Documentation (this file)
```

---

## Example Use Case: AAPL Predicting SPY

Using the analyzer, we tested whether daily closing prices of Apple Inc. (AAPL) Granger-cause the S\&P 500 ETF (SPY) over a 2020–2024 window, with a max lag of 5.

**Result:**
Granger causality testing revealed a **p-value of 0.008 at lag 2**, indicating that AAPL exhibits statistically significant predictive influence over SPY with a two-day lead.

**Interpretation:**
This suggests that prior movements in AAPL stock prices may anticipate shifts in the broader market index, making it a valuable indicator for signal engineering or lead-lag alpha strategies in systematic portfolios.

---

## Key Features

* Automates data ingestion using `yfinance`
* Applies multi-lag Granger causality testing for directionality
* Outputs clean heatmaps for fast visual evaluation
* Interactive browser app via Streamlit interface
* Extensible design for equities, crypto, FX, or macro data

---

## Installation & Execution

### 1. Set up environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run analysis

```bash
python main.py
```
## Known Issues
Streamlit Markdown Bug
If you receive this error in your browser console when running the Streamlit app:

```
SyntaxError: Invalid regular expression: invalid group specifier name
```
…it is not caused by your Python code. This is a client-side JavaScript rendering bug in Streamlit. It is triggered when st.markdown() or st.write() attempts to render malformed or overly complex Markdown (e.g., unescaped parentheses or math symbols).

Fix:
Simplify or escape special characters in Markdown blocks. You may also use st.write() as an alternative to reduce formatting conflicts with your browser’s rendering engine.
---

## Future Enhancements

* Track changes in causality over time using rolling windows
* Integrate more advanced models like Vector AutoRegression (VAR)
* Support CSV upload and user-defined datasets
* Provide downloadable reports and plots
* Add model interpretability tools and feature importance insights

---

## About the Author

Developed by Avory Campbell, B.A. Candidate in Computer Science at Columbia University, with academic focus in scientific computing, machine learning, and quantitative systems. This project reflects an intersection of statistical modeling, financial engineering, and software systems design.
Market Signal Causality Analyzer
