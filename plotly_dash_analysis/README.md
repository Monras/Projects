# Plotly + Dash Scientific and Economic Analysis

This project is a starter template for building interactive dashboards for scientific and economic analysis with Plotly and Dash.

It includes:

- A ready-to-run Dash app with interactive controls
- Reusable chart and analysis utilities
- A sample dataset for quick testing
- A project structure for data, analysis, and notebooks

## Project structure

- app.py: Dash app entry point
- requirements.txt: Python dependencies
- assets/style.css: Dashboard styling
- data/raw/: Source datasets (CSV/XLSX)
- data/processed/: Cleaned and transformed outputs
- notebooks/: Exploration notebooks
- src/data_loader.py: Data loading and sample data generation
- src/analysis.py: Summary metrics and correlation logic
- src/charts.py: Plotly figure builders

## Prerequisites

- Python 3.12+
- A virtual environment (you already have projenv in this repository)

## Quick start

Run from the repository root (the folder that contains projenv and plotly_dash_analysis):

```bash
source projenv/bin/activate
pip install -r plotly_dash_analysis/requirements.txt
cd plotly_dash_analysis
python app.py
```

Open the app at:

http://127.0.0.1:8050/

## Docker quick start

Run from the `plotly_dash_analysis` folder:

```bash
docker compose up --build
```

Open the app at:

http://127.0.0.1:8050/

Stop containers with:

```bash
docker compose down
```

### Useful Docker commands

Rebuild from scratch:

```bash
docker compose build --no-cache
```

Run in detached mode:

```bash
docker compose up -d
```

## How to use the dashboard

1. Select a variable from the Variable dropdown.
2. Change visualization mode with Chart Type (Line, Scatter, Histogram).
3. Review KPI cards at the top for latest indicator snapshots.
4. Compare relationships in the correlation heatmap.

## Working with your own data

The app is currently wired to load:

- data/raw/sample_economic_data.csv

Replace this file with your own dataset (or adjust src/data_loader.py) and keep these expected columns:

- date
- gdp_growth_pct
- inflation_pct
- unemployment_pct
- market_index
- industrial_output

Notes:

- date should be parseable as a date (for example YYYY-MM-DD).
- Numeric columns should not contain text values.

## Personal budget analysis (.ods)

This repository also supports analysis of your raw personal budget file:

- `data/raw/Summering Personlig budget.ods`

Run from the `plotly_dash_analysis` folder:

```bash
python analyze_personal_budget.py
```

Outputs are written to:

- `data/processed/personal_budget_timeseries.csv`
- `data/processed/personal_budget_analysis.md`

The analysis computes monthly cash-flow and wealth indicators such as:

- income, expenses, and net cash flow
- savings rate
- total holdings trend (12-month change)

## Extending the project

- Add new metrics in src/analysis.py.
- Add new figure functions in src/charts.py.
- Add callbacks and layout sections in app.py.
- Put cleaning pipelines in data/processed/ and notebooks in notebooks/.

## Troubleshooting

- If imports fail in editor, make sure VS Code is using the same environment as projenv.
- If port 8050 is busy, stop the other process or change the port in app.py:

```python
app.run(debug=True, port=8051)
```

- If dependency installation fails, retry after upgrading pip:

```bash
python -m pip install --upgrade pip
```

## Add this project to the Git repository

From repository root:

```bash
git add plotly_dash_analysis/README.md
git add plotly_dash_analysis
git status
```

If you want to commit immediately:

```bash
git commit -m "Add Plotly Dash analysis project scaffold and README"
```

## Next ideas

- Add forecasting models with statsmodels (ARIMA/SARIMAX)
- Add multi-page views (macro, markets, science)
- Add upload support for CSV files from the UI
- Add report export (PNG/HTML/PDF)
