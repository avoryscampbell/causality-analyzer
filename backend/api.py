# backend/api.py
from __future__ import annotations

from typing import List, Optional, Dict
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from .utils import fetch_data, fetch_many
from .causality_engine import run_granger, run_granger_symmetric_matrix

app = FastAPI(title="Market Signal Causality Analyzer API")

# CORS: allow your Vite dev server(s). Add your deployed frontend domain later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- Models ----------
class GrangerSeriesReq(BaseModel):
    series_x: List[float]
    series_y: List[float]
    max_lag: int = 5


class GrangerTickersReq(BaseModel):
    ticker_x: str
    ticker_y: str
    start: Optional[str] = None   # "YYYY-MM-DD"
    end: Optional[str] = None     # "YYYY-MM-DD"
    max_lag: int = 5


class GrangerMatrixReq(BaseModel):
    tickers: List[str]
    start: Optional[str] = None
    end: Optional[str] = None
    max_lag: int = 5
    alpha: float = 0.05


# ---------- Endpoints ----------
@app.post("/granger_series")
def granger_series(req: GrangerSeriesReq):
    """Run Granger directly on two numeric arrays."""
    try:
        sx = pd.Series(req.series_x)
        sy = pd.Series(req.series_y)
        result: Dict = run_granger(sx, sy, max_lag=req.max_lag)
        return {"result": jsonable_encoder(result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/granger_by_ticker")
def granger_by_ticker(req: GrangerTickersReq):
    """
    Fetch data for two tickers, align on time, run Granger (X causes Y).
    Returns JSON-safe dict with p-values by lag, best_lag, min_p.
    """
    try:
        df_x = fetch_data(req.ticker_x, start=req.start, end=req.end)
        df_y = fetch_data(req.ticker_y, start=req.start, end=req.end)

        # Ensure two single-column frames; rename to x/y and inner-join
        df_x = df_x[["Close"]].rename(columns={"Close": "x"})
        df_y = df_y[["Close"]].rename(columns={"Close": "y"})
        df = df_x.join(df_y, how="inner").dropna()

        if df.empty:
            raise ValueError("No overlapping data after alignment (try different dates or tickers).")

        result: Dict = run_granger(df["x"], df["y"], max_lag=req.max_lag)
        return {"result": jsonable_encoder(result)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/granger_matrix")
def granger_matrix(req: GrangerMatrixReq):
    """
    Build an NxN matrix of min p-values for causality j->i across tickers.
    Great for a heatmap in the React app.
    """
    try:
        prices = fetch_many(tuple(req.tickers), start=req.start, end=req.end)  # columns = tickers
        matrix = run_granger_symmetric_matrix(prices, max_lag=req.max_lag, alpha=req.alpha)
        return jsonable_encoder(matrix)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

