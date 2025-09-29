```markdown
# Market Signal Causality Analyzer

# A quant-ready toolkit that transforms raw financial time series into causal insights, trading signals, and interactive visualizations.

Quant-ready toolkit for discovering directional, predictive relationships between financial time series and turning them into actionable insights.  
Implements Granger causality (VAR/VECM), robust diagnostics, and interactive Plotly/Streamlit visualizations—packaged with a modern React front end for a clean UX.

> **Author:** Avory Campbell • Columbia University, CS  
> **Tech focus:** Causality discovery → Explainability → Actionable signals

---

## Highlights

- **Causality discovery**: Granger tests over configurable lags; VAR/VECM-aware workflow.
- **Data pipeline**: On-demand price fetching and alignment with clean failure modes.
- **Diagnostics**: p-values per lag, best-lag selection, quick sanity checks.
- **Visuals**: Plotly charts and Streamlit UI (lag-by-lag p-value curves, heatmaps).
- **Two UX paths**:
  - **CLI Runner**: `python main.py` runs batch analyses of ticker pairs.
  - **Streamlit App**: point-and-click exploration in the browser.
  - **(Optional)** React front end (`frontend/`) for a richer UI that can call the backend API.
- **Extensible backend**: `backend/` package with clear entry points (`utils.py`, `causality_engine.py`, `visualize.py`, `api.py`).

---

## Repository Structure

```

causality-analyzer/
├─ backend/
│  ├─ **init**.py
│  ├─ api.py                # (optional) HTTP API surface for the analyzer
│  ├─ causality_engine.py   # Granger/VAR logic
│  ├─ utils.py              # data loading, alignment, helpers
│  └─ visualize.py          # Plotly/Streamlit plotting utilities
├─ frontend/                # React + Vite + Tailwind UI
│  ├─ public/
│  ├─ src/
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.js
│  └─ tailwind.config.js
├─ app.py                   # Streamlit app (browser-based UI)
├─ main.py                  # CLI runner (batch analysis)
├─ requirements.txt         # Python deps
├─ .gitignore
├─ .env                     # (optional) local settings / keys (never commit secrets)
└─ README.md

````

---

## Quick Start

### Prereqs
- **Python** ≥ 3.10  
- **Node.js** ≥ 18 (for React front end)  
- **(macOS)** Xcode CLT recommended for native builds  

### 1) Python environment

```bash
# from repo root
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
````

> If you use Conda or Poetry, adapt accordingly.

### 2A) Run the CLI Runner (batch analysis)

`main.py` analyzes a list of predictor tickers versus a target (defaults inside file).

```bash
python main.py
```

You’ll see per-lag p-values and the best lag, e.g.:

```
=== AAPL → SPY (max_lag=5) ===
lag 1: p = 0.04321
lag 2: p = 0.07890
...
best_lag: 1, min_p: 0.04321
```

> Tweak tickers, dates, and `max_lag` in `main.py` or expose them via CLI args as a next step.

### 2B) Run the Streamlit App (interactive)

```bash
streamlit run app.py
```

* Enter two tickers (e.g., `AAPL` → `SPY`), choose date range, set `max_lag`, and click **Run**.
* You’ll get success/error feedback and (when available) Plotly visuals in-line.

### 2C) (Optional) Run the React Front End

```bash
cd frontend
npm install
npm run dev
```

Open the local URL it prints (usually `http://localhost:5173`).
The React app is wired for a richer UI; it can be connected to your Python backend via `backend/api.py` (see **API mode** below).

---

## Example: Programmatic Use

```python
from backend.utils import fetch_data
from backend.causality_engine import run_granger
from backend.visualize import plot_pvalues_by_lag

df_x = fetch_data("AAPL", start="2020-01-01", end="2024-01-01")[["Close"]].rename(columns={"Close": "x"})
df_y = fetch_data("SPY",  start="2020-01-01", end="2024-01-01")[["Close"]].rename(columns={"Close": "y"})
df = df_x.join(df_y, how="inner").dropna()

result = run_granger(df["x"], df["y"], max_lag=5)
# result: {"p_values_by_lag": {1: p1, ...}, "best_lag": int, "min_p": float}

plot_pvalues_by_lag(result, title="AAPL → SPY")  # optional
```

---

## API Mode (Optional)

If `backend/api.py` exposes a web API (e.g., FastAPI), run:

```bash
uvicorn backend.api:app --reload --port 8000
```

Then wire your React front end (`frontend/src/api.js`) to call that endpoint.

---

## Configuration

* **Dates & lags:** Edit defaults in `main.py` or pass through UI.
* **Data source:** `backend/utils.py` implements `fetch_data(...)` (e.g., via Yahoo Finance).
* **Plots:** `backend/visualize.py` centralizes Plotly/Streamlit charting.

**Environment variables (`.env`)**
Do **not** commit secrets. If any API keys are required later, keep them in `.env` and load via `os.environ` or `python-dotenv`.

---

## Roadmap (Next Upgrades)

* Stationarity checks (ADF/KPSS), automatic differencing when needed.
* Cointegration detection (Johansen) → VECM path.
* Multiple testing / FDR control across many pairs.
* Rolling windows and regime segmentation (e.g., high/low vol).
* Backtesting module with purged CV & transaction cost model.
* Exportable PDF/HTML **tear sheet** of causal edges and diagnostic plots.

---

## Contributing

1. Fork the repo and create a feature branch:

   ```bash
   git checkout -b feature/your-feature
   ```
2. Keep code modular under `backend/` and UI logic in `frontend/` or `app.py`.
3. Add/adjust tests as the project grows (e.g., `pytest`).
4. Open a PR with a clear description and before/after screenshots if UI changes.

---

## Housekeeping

* `.gitignore` excludes virtualenvs, caches, and large artifacts.
* For large datasets, consider **Git LFS**:

  ```bash
  git lfs install
  git lfs track "*.parquet" "*.csv" "reports/*.pdf"
  git add .gitattributes
  ```

---

## Screenshots

> *Add a few images/gifs here for immediate visual impact.*
> Examples:

* `docs/streamlit-home.png`
* `docs/pvalues-by-lag.png`
* `docs/heatmap.png`

```markdown
![Streamlit Home](docs/streamlit-home.png)
```

---

## License

MIT (or your choice). Add a `LICENSE` file in the repo root.
