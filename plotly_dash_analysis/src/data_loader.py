from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def get_default_data_path() -> Path:
    """Return the default location for the sample economic dataset."""
    return Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_economic_data.csv"


def generate_sample_data(periods: int = 120, seed: int = 42) -> pd.DataFrame:
    """Create a synthetic monthly dataset with macroeconomic indicators."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2015-01-01", periods=periods, freq="MS")

    gdp_growth = 2.0 + 0.5 * np.sin(np.linspace(0, 12, periods)) + rng.normal(0, 0.25, periods)
    inflation = 2.3 + 0.4 * np.sin(np.linspace(2, 15, periods)) + rng.normal(0, 0.2, periods)
    unemployment = 6.0 - 0.05 * np.arange(periods) + rng.normal(0, 0.25, periods)
    unemployment = np.clip(unemployment, 3.2, 11.0)

    market_index = 1000 + np.cumsum(rng.normal(10, 25, periods))
    industrial_output = 90 + np.cumsum(rng.normal(0.2, 0.9, periods))

    frame = pd.DataFrame(
        {
            "date": dates,
            "gdp_growth_pct": gdp_growth,
            "inflation_pct": inflation,
            "unemployment_pct": unemployment,
            "market_index": market_index,
            "industrial_output": industrial_output,
        }
    )
    return frame.round(3)


def load_or_create_data(path: Path | None = None) -> pd.DataFrame:
    """Load data if it exists; otherwise create and persist sample data."""
    target = path or get_default_data_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        data = pd.read_csv(target)
    else:
        data = generate_sample_data()
        data.to_csv(target, index=False)

    data["date"] = pd.to_datetime(data["date"])
    return data.sort_values("date").reset_index(drop=True)
