# Weyland-Yutani Mining Analytics

Task #5 (Data Engineering group): a Google Sheets generator of daily mine output and a web
dashboard that analyses it.

- **Generator (Google Sheets):** https://docs.google.com/spreadsheets/d/11bMcCAMNjKuTDoMHstHA9hZesTna60EVzw3Xp0Xsx5Q/edit
- **Dashboard:** https://task5data.streamlit.app/

## Part I: Generator

The spreadsheet is built with formulas only (no Apps Script):

| Sheet  | Purpose |
|--------|---------|
| Params | Editable parameters: start date, number of days, seed, up to 10 mine names, distribution (Normal / Uniform) with dynamic parameter labels, correlation (smoothing), day-of-week factors, daily growth (linear or compound), up to 5 events (date, duration, factor, probability or number of affected mines). |
| Hits   | Which event affects which mine (probability mode or "N mines" mode). |
| Data   | Generated daily output per mine plus Total. |
| Chart  | Line chart per mine and a column chart of the total, both updating automatically. |

How each value is generated:

1. A seeded hash-based random number (`HASHRAND` named function) keeps the data stable between
   recalculations; changing the seed produces a new data set.
2. Box-Muller turns two uniforms into a standard normal value.
3. AR(1) smoothing `z_t = rho * z_(t-1) + sqrt(1 - rho^2) * e_t` (via `SCAN`) adds correlation
   between neighbouring days.
4. The value is mapped onto the chosen distribution: `mean + sd * z` for Normal, or
   `min + (max - min) * PHI(z)` for Uniform (a Gaussian copula, so the marginal distribution stays uniform).
5. The value is multiplied by the day-of-week factor, the trend, and bell-shaped event factors
   `1 + (F - 1) * exp(-(d - c)^2 / (2 * sigma^2))`.

## Part II: Dashboard

A Streamlit app that reads the `Data` sheet live through the Google Sheets CSV endpoint.

- Mean, standard deviation, median and IQR for each mine and for the total.
- Anomaly tests with adjustable parameters:
  - IQR rule (k)
  - z-score (threshold)
  - distance from a centred moving average (window, %)
  - iterative Grubbs' test (alpha)
- An optional adjustment that removes the trend and the weekday pattern before testing, so
  regular weekend dips and growth are not reported as anomalies.
- Line, bar or stacked charts with highlighted spikes and drops, and polynomial trendlines of
  degree 1 to 4.
- Flagged days are grouped into anomaly episodes, each with a peak value, an expected value,
  a deviation, and the tests that fired.
- A one-click PDF report containing a cover page, an executive summary, statistics tables,
  charts, a section for each mine, a section for each anomaly (with a zoomed chart), and the
  methodology.

### Project structure

```
app.py                       entry point; wires the UI together
mining/                      domain package (no Streamlit dependency)
  data.py                    loading and cleaning the spreadsheet data
  stats.py                   descriptive statistics
  analysis.py                Analysis: one object holding all computed results
  detection/
    params.py                test names and DetectionParams
    outlier_tests.py         IQR, z-score, moving average, Grubbs, trend/weekday adjustment
    detector.py              runs the tests per series, flag counts
    episodes.py              groups flagged days into spike/drop episodes
  charts/
    theme.py                 palette, chart kinds, shared helpers
    interactive.py           Plotly figures for the dashboard
    static.py                matplotlib PNGs for the PDF
  report/
    builder.py               assembles the PDF
    context.py               ReportSettings, ReportContext
    components.py            reusable tables, KPI strip, banners, images
    canvas.py                page header and footer
    theme.py                 colours, page geometry, paragraph styles
    sections/                cover, summary, overview, mines, episodes, methodology
ui/                          Streamlit layer
  controls.py                sidebar controls
  data_source.py             cached loading and refresh
  header.py                  hero header and KPI cards
  overview_tab.py, mine_tab.py, anomalies_tab.py, data_tab.py
  report_panel.py            PDF generation and download
tests/                       pytest suite
```

### Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/streamlit run app.py
```

### Quality checks

```bash
.venv/bin/ruff check .
.venv/bin/pytest
```

The data source defaults to the generator above. To use another sheet, set `SHEET_URL`
(an environment variable or a Streamlit secret), or paste the URL in the sidebar. The sheet
must be shared as "Anyone with the link".

### Deploy (Streamlit Community Cloud)

1. Push this repository to GitHub.
2. Open https://share.streamlit.io, choose **Create app**, select the repository, and set the
   main file to `app.py`.
3. Under **Advanced settings**, choose Python 3.13 or newer, then deploy.
# task5data
