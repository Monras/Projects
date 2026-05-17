from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_BUDGET_FILE = "Summering Personlig budget.ods"
RAW_BUDGET_SHEET = "Mitt innehav"


LIABILITY_COLUMNS = [
    "Mastercard (swed.)",
    "Studielån (swed.)",
]


def load_personal_budget(path: Path | None = None, sheet_name: str = RAW_BUDGET_SHEET) -> pd.DataFrame:
    """Load the personal budget .ods and convert it into a monthly wide table."""
    target = path or Path(__file__).resolve().parent.parent / "data" / "raw" / RAW_BUDGET_FILE

    raw = pd.read_excel(target, sheet_name=sheet_name)
    if "Månad" not in raw.columns:
        raise ValueError("Expected a 'Månad' column in the personal budget file.")

    long_df = raw.rename(columns={"Månad": "metric"}).melt(
        id_vars="metric",
        var_name="date",
        value_name="value",
    )

    long_df["date"] = pd.to_datetime(long_df["date"], errors="coerce")
    long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
    long_df = long_df.dropna(subset=["date", "value"])

    monthly = long_df.pivot_table(index="date", columns="metric", values="value", aggfunc="last").sort_index()
    monthly.columns.name = None
    return monthly


def build_derived_budget_series(monthly: pd.DataFrame) -> pd.DataFrame:
    """Create derived financial series used in reporting."""
    result = monthly.copy()

    has_income = "Inkomst" in result.columns
    has_expenses = "Utgifter" in result.columns

    if has_income and has_expenses:
        result["net_cashflow"] = result["Inkomst"] - result["Utgifter"]
        result["savings_rate_pct"] = (result["net_cashflow"] / result["Inkomst"]).replace([pd.NA], pd.NA) * 100

    if "totalt innehav" in result.columns:
        result["net_worth_proxy"] = result["totalt innehav"]

    existing_liabilities = [c for c in LIABILITY_COLUMNS if c in result.columns]
    if existing_liabilities:
        result["known_liabilities"] = result[existing_liabilities].sum(axis=1, min_count=1)

    return result


def compute_budget_summary(derived: pd.DataFrame) -> dict[str, float | str]:
    """Compute core summary metrics for personal budget analysis."""
    if derived.empty:
        raise ValueError("No usable data points were found in the personal budget dataset.")

    latest_date = derived.index.max()
    summary: dict[str, float | str] = {
        "latest_date": latest_date.strftime("%Y-%m-%d"),
        "months_observed": int(len(derived)),
    }

    if "Inkomst" in derived.columns:
        summary["latest_income"] = float(derived["Inkomst"].dropna().iloc[-1])
        summary["income_12m_avg"] = float(derived["Inkomst"].dropna().tail(12).mean())

    if "Utgifter" in derived.columns:
        summary["latest_expenses"] = float(derived["Utgifter"].dropna().iloc[-1])
        summary["expenses_12m_avg"] = float(derived["Utgifter"].dropna().tail(12).mean())

    if "net_cashflow" in derived.columns:
        summary["latest_net_cashflow"] = float(derived["net_cashflow"].dropna().iloc[-1])
        summary["net_cashflow_12m_avg"] = float(derived["net_cashflow"].dropna().tail(12).mean())

    if "savings_rate_pct" in derived.columns:
        summary["savings_rate_12m_avg_pct"] = float(derived["savings_rate_pct"].dropna().tail(12).mean())

    if "net_worth_proxy" in derived.columns and len(derived["net_worth_proxy"].dropna()) > 12:
        nw = derived["net_worth_proxy"].dropna()
        summary["latest_net_worth_proxy"] = float(nw.iloc[-1])
        summary["net_worth_12m_change_pct"] = float((nw.iloc[-1] / nw.iloc[-13] - 1) * 100)

    return summary


def build_markdown_report(summary: dict[str, float | str]) -> str:
    """Render a concise markdown report from summary metrics."""

    def fmt_currency(key: str) -> str:
        value = summary.get(key)
        if value is None:
            return "n/a"
        return f"{value:,.0f} SEK"

    def fmt_pct(key: str) -> str:
        value = summary.get(key)
        if value is None:
            return "n/a"
        return f"{value:.2f}%"

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
