"""Personal Budget Dashboard - Dash web application.

This module implements an interactive dashboard for analyzing personal budget data using Dash.
It displays key financial metrics, allows filtering by budget variables, and provides
multiple visualization types (line, bar, area charts).
"""
from __future__ import annotations

import os

from dash import Dash, Input, Output, dcc, html

from src.charts import budget_timeseries_chart, income_expense_comparison_chart
from src.personal_budget_analysis import (
    build_derived_budget_series,
    compute_budget_summary,
    load_personal_budget,
)

# Initialize global state variables for the budget dashboard
budget_available = True  # Flag indicating if budget data loaded successfully
budget_error = ""  # Error message if budget data loading failed
budget_chart_df = None  # DataFrame containing processed budget data for charts
budget_summary: dict[str, float | str] = {}  # Dictionary of summary metrics
budget_variable_options: list[dict[str, str]] = []  # Available budget variables for dropdown

# Attempt to load and process personal budget data
try:
    budget_monthly = load_personal_budget().reset_index()
    budget_derived = build_derived_budget_series(budget_monthly)
    budget_summary = compute_budget_summary(budget_derived.set_index("date"))
    budget_chart_df = budget_derived

    # Define available budget metrics for visualization
    candidate_budget_vars = [
        "Inkomst",
        "Utgifter",
        "net_cashflow",
        "Sparande",
        "totalt innehav",
        "known_liabilities",
    ]
    # Build dropdown options from available columns
    budget_variable_options = [
        {"label": col.replace("_", " ").title(), "value": col}
        for col in candidate_budget_vars
        if col in budget_chart_df.columns
    ]
except Exception as exc:  # pragma: no cover - defensive app startup fallback
    budget_available = False
    budget_error = str(exc)

# Available chart type options for the budget visualization
budget_chart_type_options = [
    {"label": "Line", "value": "line"},
    {"label": "Bar", "value": "bar"},
    {"label": "Area", "value": "area"},
]


def _fmt_sek(value: float | str | None) -> str:
    """Format a numeric value as Swedish Kronor (SEK).
    
    Args:
        value: Numeric value to format, or None
        
    Returns:
        Formatted string with SEK currency, or 'n/a' if value is None
    """
    if value is None:
        return "n/a"
    return f"{float(value):,.0f} SEK"


def _fmt_pct(value: float | str | None) -> str:
    """Format a numeric value as percentage.
    
    Args:
        value: Numeric value to format, or None
        
    Returns:
        Formatted string with percentage (2 decimal places), or 'n/a' if value is None
    """
    if value is None:
        return "n/a"
    return f"{float(value):.2f}%"


app = Dash(__name__)
app.title = "Personal Budget Dashboard"

app.layout = html.Div(
    className="page",
    children=[
        html.Header(
            className="header",
            children=[
                html.H1("Personal Budget Analysis Dashboard"),
                html.P("Interactive budget tracking with Plotly + Dash"),
            ],
        ),
        html.Section(
            className="metrics-grid",
            children=(
                [
                    html.Div([
                        html.H3("Latest Income"),
                        html.P(_fmt_sek(budget_summary.get("latest_income"))),
                    ], className="metric-card"),
                    html.Div([
                        html.H3("Latest Expenses"),
                        html.P(_fmt_sek(budget_summary.get("latest_expenses"))),
                    ], className="metric-card"),
                    html.Div([
                        html.H3("12M Savings Rate"),
                        html.P(_fmt_pct(budget_summary.get("savings_rate_12m_avg_pct"))),
                    ], className="metric-card"),
                    html.Div([
                        html.H3("12M Holdings Change"),
                        html.P(_fmt_pct(budget_summary.get("net_worth_12m_change_pct"))),
                    ], className="metric-card"),
                ]
                if budget_available
                else [
                    html.Div([
                        html.H3("Personal Budget Data"),
                        html.P(f"Could not load budget file: {budget_error}"),
                    ], className="metric-card")
                ]
            ),
        ),
        html.Section(
            className="controls",
            children=[
                html.Div([
                    html.Label("Budget Variable"),
                    dcc.Dropdown(
                        id="budget-variable-dropdown",
                        options=budget_variable_options,
                        value=(
                            budget_variable_options[0]["value"]
                            if budget_variable_options
                            else None
                        ),
                        clearable=False,
                    ),
                ]),
                html.Div([
                    html.Label("Chart Type"),
                    dcc.RadioItems(
                        id="budget-chart-type-radio",
                        options=budget_chart_type_options,
                        value="line",
                        inline=True,
                    ),
                ]),
            ],
        ),
        html.Section(
            className="chart-grid",
            children=[
                dcc.Graph(id="budget-main-chart"),
                dcc.Graph(
                    id="budget-income-expense-chart",
                    figure=(
                        income_expense_comparison_chart(budget_chart_df)
                        if budget_available and budget_chart_df is not None
                        else None
                    ),
                ),
            ],
        ),
    ],
)


# Callback to update the main budget chart when user changes variable or chart type
@app.callback(
    Output("budget-main-chart", "figure"),
    Input("budget-variable-dropdown", "value"),
    Input("budget-chart-type-radio", "value"),
)
def update_budget_chart(selected_variable: str | None, selected_chart_type: str):
    """Update the main chart based on selected variable and chart type.
    
    Args:
        selected_variable: Name of the budget variable to display
        selected_chart_type: Type of chart (line, bar, or area)
        
    Returns:
        Plotly figure object with the updated chart
    """
    # Fallback to reloading data if not yet available
    if budget_chart_df is None:
        return budget_timeseries_chart(
            load_personal_budget().reset_index(),
            "totalt innehav",
            "line",
        )

    # Default to total holdings if no variable selected or variable not in data
    if not selected_variable or selected_variable not in budget_chart_df.columns:
        selected_variable = "totalt innehav"

    return budget_timeseries_chart(budget_chart_df, selected_variable, selected_chart_type)


# Run the Dash application with environment-based configuration
if __name__ == "__main__":
    # Debug mode, host, and port can be configured via environment variables
    app.run(
        debug=os.getenv("DASH_DEBUG", "false").lower() == "true",
        host=os.getenv("DASH_HOST", "0.0.0.0"),
        port=int(os.getenv("DASH_PORT", "8050")),
    )
