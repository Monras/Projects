from __future__ import annotations

import pandas as pd


def compute_summary_metrics(df: pd.DataFrame) -> dict[str, float]:
    """Build dashboard summary metrics from the latest observation."""
    last = df.iloc[-1]
    return {
        "latest_gdp_growth": float(last["gdp_growth_pct"]),
        "latest_inflation": float(last["inflation_pct"]),
        "latest_unemployment": float(last["unemployment_pct"]),
        "market_index_change_12m": float(df["market_index"].pct_change(12).iloc[-1] * 100),
    }


def build_correlation_table(df: pd.DataFrame) -> pd.DataFrame:
    """Compute correlation across numerical indicators."""
    numeric_cols = [
        "gdp_growth_pct",
        "inflation_pct",
        "unemployment_pct",
        "market_index",
        "industrial_output",
    ]
    return df[numeric_cols].corr().round(3)
