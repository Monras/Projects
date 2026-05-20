"""Personal budget data processing and analysis.

Handles loading personal budget data from CSV files, computing derived financial
metrics (net cashflow, savings rate, etc.), and generating summary statistics.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


# Configuration for budget file
RAW_BUDGET_FILE = "personal_budget.csv"

# List of liability columns to aggregate for total known liabilities
LIABILITY_COLUMNS = [
    "Studielån (swed.)",
]


def load_personal_budget(path: Path | None = None) -> pd.DataFrame:
    """Load the personal budget CSV with months as rows and metrics as columns.
    
    Args:
        path: Optional path to budget file. Uses default if not specified.
        
    Returns:
        DataFrame indexed by date with budget metrics as columns
    """
    target = path or Path(__file__).resolve().parent.parent / "data" / "raw" / RAW_BUDGET_FILE

    # Read CSV with first column as index (dates)
    df = pd.read_csv(target, index_col=0)
    
    # Convert index to datetime
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df.dropna(how="all")  # Remove rows that are all NaN
    
    # Ensure all values are numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df.sort_index()


def build_derived_budget_series(monthly: pd.DataFrame) -> pd.DataFrame:
    """Create derived financial series used in reporting.
    
    Computes additional financial metrics from base budget columns:
    - Net cashflow (income - expenses)
    - Savings rate percentage
    - Total liabilities aggregation
    
    Args:
        monthly: DataFrame with raw budget metrics
        
    Returns:
        DataFrame with original and derived columns
    """
    result = monthly.copy()

    # Compute net cashflow if income and expenses are available
    has_income = "Inkomst" in result.columns
    has_expenses = "Utgifter" in result.columns

    # Compute cashflow and savings rate only when both inputs exist.
    if has_income and has_expenses:
        result["net_cashflow"] = result["Inkomst"] - result["Utgifter"]
        result["savings_rate_pct"] = (result["net_cashflow"] / result["Inkomst"]).replace([pd.NA], pd.NA) * 100

    # Add net worth proxy if total holdings available
    if "totalt innehav" in result.columns:
        result["net_worth_proxy"] = result["totalt innehav"]

    # Aggregate known liabilities from configured columns
    existing_liabilities = [c for c in LIABILITY_COLUMNS if c in result.columns]
    if existing_liabilities:
        result["known_liabilities"] = result[existing_liabilities].sum(axis=1, min_count=1)

    return result


def compute_budget_summary(derived: pd.DataFrame) -> dict[str, float | str]:
    """Compute core summary metrics for personal budget analysis.
    
    Extracts latest values and 12-month averages for key budget metrics
    to display on the dashboard.
    
    Args:
        derived: DataFrame with derived budget series (output from build_derived_budget_series)
        
    Returns:
        Dictionary containing summary metrics for dashboard display
        
    Raises:
        ValueError: If input DataFrame is empty
    """
    if derived.empty:
        raise ValueError("No usable data points were found in the personal budget dataset.")

    # Initialize summary with date information
    latest_date = derived.index.max()
    summary: dict[str, float | str] = {
        "latest_date": latest_date.strftime("%Y-%m-%d"),
        "months_observed": int(len(derived)),
    }

    # Extract income metrics if available
    if "Inkomst" in derived.columns:
        summary["latest_income"] = float(derived["Inkomst"].dropna().iloc[-1])
        summary["income_12m_avg"] = float(derived["Inkomst"].dropna().tail(12).mean())

    # Extract expense metrics if available
    if "Utgifter" in derived.columns:
        summary["latest_expenses"] = float(derived["Utgifter"].dropna().iloc[-1])
        summary["expenses_12m_avg"] = float(derived["Utgifter"].dropna().tail(12).mean())

    # Extract cashflow metrics if available
    if "net_cashflow" in derived.columns:
        summary["latest_net_cashflow"] = float(derived["net_cashflow"].dropna().iloc[-1])
        summary["net_cashflow_12m_avg"] = float(derived["net_cashflow"].dropna().tail(12).mean())

    # Extract savings rate metrics if available
    if "savings_rate_pct" in derived.columns:
        summary["savings_rate_12m_avg_pct"] = float(derived["savings_rate_pct"].dropna().tail(12).mean())

    # Extract net worth change if sufficient history available (>12 months)
    if "net_worth_proxy" in derived.columns and len(derived["net_worth_proxy"].dropna()) > 12:
        nw = derived["net_worth_proxy"].dropna()
        summary["latest_net_worth_proxy"] = float(nw.iloc[-1])
        summary["net_worth_12m_change_pct"] = float((nw.iloc[-1] / nw.iloc[-13] - 1) * 100)

    return summary


def build_markdown_report(summary: dict[str, float | str]) -> str:
    """Render a concise markdown report from summary metrics.
    
    Args:
        summary: Dictionary of summary metrics from compute_budget_summary
        
    Returns:
        Formatted markdown string with budget analysis report
    """
    # Helper to format currency values
    def fmt_currency(key: str) -> str:
        # Keep report generation resilient when a metric is unavailable.
        value = summary.get(key)
        if value is None:
            return "n/a"
        return f"{value:,.0f} SEK"

    # Helper to format percentage values
    def fmt_pct(key: str) -> str:
        value = summary.get(key)
        if value is None:
            return "n/a"
        return f"{value:.2f}%"

    # Build markdown report sections
    lines = [
        "# Personal Budget Economic Analysis",
        "",
        f"Analysis month: **{summary.get('latest_date', 'n/a')}**",
        f"Observed months: **{summary.get('months_observed', 'n/a')}**",
        "",
        "## Cash Flow",
        f"- Latest income: **{fmt_currency('latest_income')}**",
        f"- Latest expenses: **{fmt_currency('latest_expenses')}**",
        f"- Latest net cash flow: **{fmt_currency('latest_net_cashflow')}**",
        f"- 12M average net cash flow: **{fmt_currency('net_cashflow_12m_avg')}**",
        f"- 12M average savings rate: **{fmt_pct('savings_rate_12m_avg_pct')}**",
        "",
        "## Wealth",
        f"- Latest total holdings (proxy): **{fmt_currency('latest_net_worth_proxy')}**",
        f"- 12M change in total holdings: **{fmt_pct('net_worth_12m_change_pct')}**",
    ]

    return "\n".join(lines)
