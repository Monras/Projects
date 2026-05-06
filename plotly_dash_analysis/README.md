# Plotly + Dash Project for Scientific and Economic Analysis

This starter project gives you a clean base to build interactive dashboards for scientific and economic data analysis.

## Project structure

- `app.py`: Dash application entry point
- `src/data_loader.py`: load dataset or generate synthetic sample data
- `src/analysis.py`: summary metrics and correlations
- `src/charts.py`: reusable Plotly chart functions
- `data/raw/`: source datasets (CSV, XLSX, etc.)
- `data/processed/`: cleaned and transformed data
- `notebooks/`: exploratory analysis notebooks
- `assets/style.css`: dashboard styling

## 1) Activate your virtual environment

From `/home/mans/Projects`:

```bash
source projenv/bin/activate
```

## 2) Install dependencies

```bash
pip install -r plotly_dash_analysis/requirements.txt
```

## 3) Run the dashboard

```bash
cd plotly_dash_analysis
python app.py
```

Open: http://127.0.0.1:8050/

## 4) Add your own dataset

Replace `data/raw/sample_economic_data.csv` with your own file and keep at least one date column and numeric indicators.

Expected columns for the current demo:
- `date`
- `gdp_growth_pct`
- `inflation_pct`
- `unemployment_pct`
- `market_index`
- `industrial_output`

## Next ideas

- Add time-series forecasting with statsmodels (ARIMA/SARIMAX)
- Add sector-level economic indicators
- Build scenario comparison tabs (baseline vs stress case)
- Export figures and reports automatically
