"""Data loading and generation utilities.

Provides functions for loading and creating economic datasets.
Supports both loading existing CSV files and generating synthetic macroeconomic data.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def get_default_data_path() -> Path:
    """Return the default location for the sample economic dataset.
    
    Returns:
        Path object pointing to data/raw/sample_economic_data.csv
    """
    return Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_economic_data.csv"


def generate_sample_data(periods: int = 120, seed: int = 42) -> pd.DataFrame:
    """Create a synthetic monthly dataset with macroeconomic indicators.
    
    Generates realistic-looking economic data with seasonal patterns and random noise.
    
    Args:
        periods: Number of monthly periods to generate (default: 120 months = 10 years)
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with date and economic indicator columns
    """
    # Initialize random generator with seed for reproducibility
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2015-01-01", periods=periods, freq="MS")

    # Generate realistic macroeconomic indicators with seasonal patterns
    gdp_growth = 2.0 + 0.5 * np.sin(np.linspace(0, 12, periods)) + rng.normal(0, 0.25, periods)
    inflation = 2.3 + 0.4 * np.sin(np.linspace(2, 15, periods)) + rng.normal(0, 0.2, periods)
    unemployment = 6.0 - 0.05 * np.arange(periods) + rng.normal(0, 0.25, periods)
    unemployment = np.clip(unemployment, 3.2, 11.0)  # Constrain to realistic range

    # Generate cumulative time series for market and industrial data
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
    """Load data if it exists; otherwise create and persist sample data.
    
    Args:
        path: Optional path to CSV file. If None, uses default data path.
        
    Returns:
        DataFrame with economic data, sorted by date
    """
    # Use default path if not specified
    target = path or get_default_data_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    # Load existing data or generate new sample data
    if target.exists():
        data = pd.read_csv(target)
    else:
        data = generate_sample_data()
        data.to_csv(target, index=False)

    # Parse date column and sort chronologically
    data["date"] = pd.to_datetime(data["date"])
    return data.sort_values("date").reset_index(drop=True)
