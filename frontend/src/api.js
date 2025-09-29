import axios from "axios";

// Use your backend URL from .env
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

// Function for /granger_by_ticker
export async function grangerByTickers({ ticker_x, ticker_y, start, end, max_lag }) {
  const res = await api.post("/granger_by_ticker", {
    ticker_x,
    ticker_y,
    start,
    end,
    max_lag,
  });
  return res.data;
}

