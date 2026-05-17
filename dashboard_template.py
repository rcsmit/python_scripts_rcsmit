"""
dashboard_template.py
=====================
A zero-extra-packages local web dashboard using only Python stdlib.
Charts are rendered by Plotly.js loaded from CDN.

Pattern:
  - Python side  → query / compute data, serve it as JSON via /api/data
  - Browser side → fetch JSON, build Plotly charts + tables with vanilla JS

Usage:
  python dashboard_template.py          # serves on http://localhost:8080
  python dashboard_template.py 9000     # custom port
"""

import json
import random
import webbrowser
import threading
import time
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, date, timedelta

# ── Config ────────────────────────────────────────────────────────────────────

PORT = 8080
random.seed(42)

CATEGORIES = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]


# ── Data layer ────────────────────────────────────────────────────────────────

def get_data() -> dict:
    """Generate fake data — replace this function with your real data source."""

    today = date.today()

    # Daily totals for the last 90 days
    daily = []
    base_a, base_b = 400, 250
    for i in range(90):
        day = today - timedelta(days=89 - i)
        base_a += random.randint(-30, 35)
        base_b += random.randint(-20, 25)
        daily.append({
            "day":     day.isoformat(),
            "value_a": max(0, base_a + random.randint(-50, 50)),
            "value_b": max(0, base_b + random.randint(-40, 40)),
        })

    # Breakdown by category
    by_category = [
        {
            "category": cat,
            "count":    random.randint(10, 200),
            "total_a":  random.randint(1000, 20000),
        }
        for cat in CATEGORIES
    ]
    by_category.sort(key=lambda r: r["total_a"], reverse=True)

    # Recent rows (last 50)
    recent = []
    for i in range(50):
        day = today - timedelta(days=random.randint(0, 30))
        recent.append({
            "id":       1000 + i,
            "date_col": day.isoformat(),
            "category": random.choice(CATEGORIES),
            "value_a":  random.randint(10, 999),
            "value_b":  random.randint(5, 499),
        })
    recent.sort(key=lambda r: r["date_col"], reverse=True)

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "daily":        daily,
        "by_category":  by_category,
        "recent":       recent,
    }


# ── HTML / JS template ────────────────────────────────────────────────────────
# Everything between the triple-quotes is served as index.html.
# Edit the JS section to match your data shape from get_data() above.

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard</title>
<!-- Plotly from CDN — no npm, no bundler -->
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  :root {
    --bg:      #0f1117;
    --card:    #1a1d27;
    --border:  #2a2d3a;
    --text:    #e2e8f0;
    --muted:   #8892a4;
    --accent:  #d97757;
    --blue:    #4f8ef7;
    --green:   #4ade80;
    --red:     #f87171;
    --font:    -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: var(--font); font-size: 14px; }

  /* ── Header ── */
  header {
    background: var(--card); border-bottom: 1px solid var(--border);
    padding: 14px 28px; display: flex; align-items: center; justify-content: space-between;
  }
  header h1 { font-size: 17px; font-weight: 700; color: var(--accent); letter-spacing: -0.3px; }
  #meta { color: var(--muted); font-size: 12px; }

  /* ── Layout ── */
  main { max-width: 1400px; margin: 0 auto; padding: 24px 28px; }

  /* ── KPI cards ── */
  .kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px; margin-bottom: 24px;
  }
  .kpi {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 18px;
  }
  .kpi .label { font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin-bottom: 6px; }
  .kpi .value { font-size: 26px; font-weight: 700; line-height: 1; }
  .kpi .sub   { font-size: 11px; color: var(--muted); margin-top: 5px; }

  /* ── Chart grid ── */
  .chart-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 16px; margin-bottom: 24px;
  }
  .chart-grid.single { grid-template-columns: 1fr; }
  .card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px;
  }
  .card h2 {
    font-size: 12px; font-weight: 600; text-transform: uppercase;
    letter-spacing: .07em; color: var(--muted); margin-bottom: 14px;
  }
  .plot-container { width: 100%; height: 280px; }

  /* ── Table ── */
  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  thead th {
    text-align: left; padding: 8px 12px; font-size: 11px;
    text-transform: uppercase; letter-spacing: .06em;
    color: var(--muted); border-bottom: 1px solid var(--border);
  }
  tbody td { padding: 9px 12px; border-bottom: 1px solid var(--border); }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: rgba(255,255,255,0.025); }
  .badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 600;
    background: rgba(79,142,247,0.15); color: var(--blue);
  }
  .num { font-family: monospace; }
  .muted { color: var(--muted); }
  .green { color: var(--green); }

  /* ── Error ── */
  #error { display: none; padding: 30px; color: var(--red); font-size: 15px; }

  @media (max-width: 768px) {
    .chart-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<header>
  <h1>📊 My Dashboard</h1>
  <span id="meta">Loading…</span>
</header>

<main>
  <div id="error"></div>

  <!-- KPI row -->
  <div class="kpi-row" id="kpi-row">
    <div class="kpi"><div class="label">Total rows</div>   <div class="value" id="kpi-rows">—</div></div>
    <div class="kpi"><div class="label">Sum value A</div>  <div class="value" id="kpi-a">—</div></div>
    <div class="kpi"><div class="label">Sum value B</div>  <div class="value" id="kpi-b">—</div></div>
    <div class="kpi"><div class="label">Categories</div>   <div class="value" id="kpi-cats">—</div></div>
  </div>

  <!-- Charts -->
  <div class="chart-grid">
    <div class="card">
      <h2>Daily Values</h2>
      <div id="chart-daily" class="plot-container"></div>
    </div>
    <div class="card">
      <h2>By Category</h2>
      <div id="chart-category" class="plot-container"></div>
    </div>
  </div>

  <!-- Recent rows table -->
  <div class="card">
    <h2>Recent rows</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th><th>Date</th><th>Category</th>
            <th>Value A</th><th>Value B</th>
          </tr>
        </thead>
        <tbody id="table-body"></tbody>
      </table>
    </div>
  </div>
</main>

<script>
// ── Plotly shared theme ────────────────────────────────────────────────────
const THEME = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor:  'rgba(0,0,0,0)',
  font:          { color: '#8892a4', size: 11 },
  margin:        { t: 10, r: 10, b: 40, l: 50 },
  xaxis: { gridcolor: '#2a2d3a', linecolor: '#2a2d3a', tickcolor: '#2a2d3a' },
  yaxis: { gridcolor: '#2a2d3a', linecolor: '#2a2d3a', tickcolor: '#2a2d3a' },
  legend: { bgcolor: 'rgba(0,0,0,0)', font: { size: 11 } },
  colorway: ['#4f8ef7','#d97757','#4ade80','#f87171','#a78bfa','#38bdf8'],
};

const PLOTLY_CONFIG = { displayModeBar: false, responsive: true };

// ── Helpers ────────────────────────────────────────────────────────────────
function fmt(n) {
  if (n == null) return '—';
  if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(2) + 'M';
  if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return String(n);
}

// ── Renderers ──────────────────────────────────────────────────────────────

function renderKPIs(daily, byCategory, recent) {
  const totalA = daily.reduce((s, d) => s + (d.value_a || 0), 0);
  const totalB = daily.reduce((s, d) => s + (d.value_b || 0), 0);
  document.getElementById('kpi-rows').textContent  = fmt(recent.length);
  document.getElementById('kpi-a').textContent     = fmt(totalA);
  document.getElementById('kpi-b').textContent     = fmt(totalB);
  document.getElementById('kpi-cats').textContent  = byCategory.length;
}

function renderDailyChart(daily) {
  const layout = {
    ...THEME,
    barmode: 'stack',
    xaxis: { ...THEME.xaxis, type: 'date' },
  };
  const traces = [
    {
      type: 'bar', name: 'Value A',
      x: daily.map(d => d.day), y: daily.map(d => d.value_a),
      marker: { color: '#4f8ef7' },
    },
    {
      type: 'bar', name: 'Value B',
      x: daily.map(d => d.day), y: daily.map(d => d.value_b),
      marker: { color: '#d97757' },
    },
  ];
  Plotly.react('chart-daily', traces, layout, PLOTLY_CONFIG);
}

function renderCategoryChart(byCategory) {
  const layout = {
    ...THEME,
    margin: { t: 10, r: 10, b: 10, l: 10 },
  };
  const trace = [{
    type: 'pie',
    labels: byCategory.map(c => c.category),
    values: byCategory.map(c => c.total_a),
    hole: 0.45,
    textinfo: 'percent',
    textfont: { size: 11 },
    marker: { colors: ['#4f8ef7','#d97757','#4ade80','#f87171','#a78bfa','#38bdf8','#fbbf24','#34d399','#e879f9','#fb923c'] }
  }];
  Plotly.react('chart-category', trace, layout, PLOTLY_CONFIG);
}

function renderTable(recent) {
  document.getElementById('table-body').innerHTML = recent.map(r => `
    <tr>
      <td class="num muted">${r.id}</td>
      <td class="muted">${r.date_col}</td>
      <td><span class="badge">${r.category}</span></td>
      <td class="num">${fmt(r.value_a)}</td>
      <td class="num">${fmt(r.value_b)}</td>
    </tr>
  `).join('');
}

// ── Load data & render ─────────────────────────────────────────────────────
async function loadData() {
  try {
    const resp = await fetch('/api/data');
    const d    = await resp.json();

    if (d.error) {
      document.getElementById('error').style.display = 'block';
      document.getElementById('error').textContent = '⚠ ' + d.error;
      return;
    }

    document.getElementById('meta').textContent =
      'Updated: ' + d.generated_at + ' · auto-refresh 30 s';

    renderKPIs(d.daily, d.by_category, d.recent);
    renderDailyChart(d.daily);
    renderCategoryChart(d.by_category);
    renderTable(d.recent);

  } catch(err) {
    console.error('Fetch failed:', err);
  }
}

loadData();
setInterval(loadData, 30_000);   // auto-refresh every 30 s
</script>
</body>
</html>
"""


# ── HTTP server ────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    """Minimal handler: serves index.html and /api/data."""

    def log_message(self, fmt, *args):
        # Suppress per-request noise; remove this line to re-enable
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type",   "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/api/data":
            data = get_data()
            body = json.dumps(data, default=str).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type",   "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        else:
            self.send_response(404)
            self.end_headers()


def serve(port: int = PORT):
    server = HTTPServer(("localhost", port), Handler)
    url = f"http://localhost:{port}"
    print(f"Dashboard → {url}")
    print("Press Ctrl+C to stop.\n")

    # Open browser after a short delay so the server is ready
    def _open():
        time.sleep(0.8)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve(port)
