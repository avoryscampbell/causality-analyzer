import { useState, useMemo } from "react";
import { useMutation } from "@tanstack/react-query";
import Plot from "react-plotly.js";
import { grangerByTickers } from "./api";

export default function App() {
  const [tickerX, setTickerX] = useState("AAPL");
  const [tickerY, setTickerY] = useState("SPY");
  const [start, setStart] = useState("2023-01-01");
  const [end, setEnd] = useState("2024-06-01");
  const [maxLag, setMaxLag] = useState(5);

  const mutation = useMutation({ mutationFn: grangerByTickers });

  const result = mutation.data?.result || null;

  const { xLags, yPvals } = useMemo(() => {
    const pmap = result?.p_values_by_lag || {};
    const entries = Object.entries(pmap).sort(
      (a, b) => Number(a[0]) - Number(b[0])
    );
    return {
      xLags: entries.map(([lag]) => Number(lag)),
      yPvals: entries.map(([, p]) => Number(p)),
    };
  }, [result]);

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate({
      ticker_x: tickerX.trim().toUpperCase(),
      ticker_y: tickerY.trim().toUpperCase(),
      start,
      end,
      max_lag: Number(maxLag),
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="p-5 border-b bg-white">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold">Market Signal Causality Analyzer</h1>
          <p className="text-sm text-gray-600">
            Visualize Granger-causality p-values by lag between two tickers.
          </p>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-6 grid grid-cols-12 gap-6">
        {/* Controls */}
        <aside className="col-span-12 md:col-span-4 bg-white border rounded-xl p-4 space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Predictor (X)</label>
              <input
                className="w-full border rounded-md px-3 py-2"
                value={tickerX}
                onChange={(e) => setTickerX(e.target.value)}
                placeholder="e.g. AAPL"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Target (Y)</label>
              <input
                className="w-full border rounded-md px-3 py-2"
                value={tickerY}
                onChange={(e) => setTickerY(e.target.value)}
                placeholder="e.g. SPY"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium mb-1">Start</label>
                <input
                  type="date"
                  className="w-full border rounded-md px-3 py-2"
                  value={start}
                  onChange={(e) => setStart(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">End</label>
                <input
                  type="date"
                  className="w-full border rounded-md px-3 py-2"
                  value={end}
                  onChange={(e) => setEnd(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Max Lag</label>
              <input
                type="number"
                min={1}
                max={20}
                className="w-full border rounded-md px-3 py-2"
                value={maxLag}
                onChange={(e) => setMaxLag(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={mutation.isPending}
              className="w-full bg-black text-white rounded-md py-2 font-medium disabled:opacity-60"
            >
              {mutation.isPending ? "Analyzing…" : "Run Analysis"}
            </button>

            {mutation.isError && (
              <p className="text-sm text-red-600">
                Error: {mutation.error?.response?.data?.detail || mutation.error.message}
              </p>
            )}
          </form>
        </aside>

        {/* Visualization */}
        <main className="col-span-12 md:col-span-8 space-y-4">
          {!result && !mutation.isPending && (
            <div className="bg-white border rounded-xl p-4">
              <p className="text-gray-600">
                Enter inputs and click <span className="font-medium">Run Analysis</span>.
              </p>
            </div>
          )}

          {mutation.isPending && (
            <div className="bg-white border rounded-xl p-4">
              <p className="text-gray-900">Computing…</p>
            </div>
          )}

          {result && (
            <>
              <div className="bg-white border rounded-xl p-4">
                <h2 className="font-semibold mb-2">
                  {tickerX.toUpperCase()} → {tickerY.toUpperCase()} p-values by lag
                </h2>
                <Plot
                  data={[
                    {
                      type: "bar",
                      x: xLags,
                      y: yPvals,
                      name: "p-value",
                      hovertemplate: "lag %{x}<br>p=%{y:.5f}<extra></extra>",
                    },
                    // significance line at 0.05
                    {
                      type: "scatter",
                      mode: "lines",
                      x: xLags.length ? [Math.min(...xLags), Math.max(...xLags)] : [1, Number(maxLag)],
                      y: [0.05, 0.05],
                      name: "α = 0.05",
                    },
                  ]}
                  layout={{
                    height: 420,
                    margin: { l: 60, r: 20, t: 30, b: 50 },
                    xaxis: { title: "Lag" },
                    yaxis: { title: "p-value", rangemode: "tozero" },
                    showlegend: true,
                  }}
                  style={{ width: "100%" }}
                  useResizeHandler
                  className="w-full"
                />
              </div>

              <div className="bg-white border rounded-xl p-4">
                <h3 className="font-semibold mb-2">Summary</h3>
                <div className="text-sm">
                  <div>
                    <span className="font-medium">best_lag:</span> {result.best_lag}
                  </div>
                  <div>
                    <span className="font-medium">min_p:</span>{" "}
                    {Number(result.min_p).toFixed(5)}
                  </div>
                </div>

                <h4 className="font-semibold mt-4 mb-1">Table</h4>
                <table className="text-sm">
                  <tbody>
                    {xLags.map((lag, idx) => (
                      <tr key={lag}>
                        <td className="pr-6">lag {lag}</td>
                        <td>{yPvals[idx].toFixed(5)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

