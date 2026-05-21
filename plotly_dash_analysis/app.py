"""Personal Budget Dashboard - Dash web application.

This module implements an interactive dashboard for analyzing personal budget data using Dash.
It displays key financial metrics, allows filtering by budget variables, and provides
multiple visualization types (line, bar, area charts).
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from dash import Dash, Input, Output, State, dcc, html, callback, ALL
import pandas as pd

from src.charts import budget_timeseries_chart, income_expense_comparison_chart
from src.personal_budget_analysis import (
    RAW_BUDGET_FILE,
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
    budget_monthly = load_personal_budget()
    budget_derived = build_derived_budget_series(budget_monthly)
    budget_summary = compute_budget_summary(budget_derived)
    budget_chart_df = budget_derived.reset_index()
    # Rename the index column to "date" - the index name comes from the CSV's first column
    if budget_chart_df.columns[0] != "date":
        budget_chart_df = budget_chart_df.rename(columns={budget_chart_df.columns[0]: "date"})

    # Define available budget metrics for visualization
    candidate_budget_vars = [
        "Inkomst",
        "Utgifter",
        "Sparkonto (swed.)",
        "Mastercard (swed.)",
        "Aktier/Fonder (Avanza)",      
        "SBAB",    
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
        html.Section(
            className="new-entry-section",
            children=[
                html.H2("Add New Month Entry"),
                html.P("Enter budget data for a new month. This will be saved to the raw data file."),
                html.Div(
                    className="entry-form",
                    children=[
                        html.Div([
                            html.Label("Month (YYYY-MM format)"),
                            dcc.Input(
                                id="new-month-input",
                                type="text",
                                placeholder=datetime.now().strftime("%Y-%m"),
                                style={"width": "100%", "padding": "8px", "marginBottom": "10px"},
                            ),
                        ]),
                        html.Div(
                            id="metric-inputs-container",
                            children=(
                                [
                                    html.Div([
                                        html.Label(col),
                                        dcc.Input(
                                            id={"type": "metric-input", "index": col},
                                            type="number",
                                            placeholder="0",
                                            step=1000,
                                            style={"width": "100%", "padding": "8px", "marginBottom": "10px"},
                                        ),
                                    ])
                                    for col in candidate_budget_vars
                                                                ]
                                if budget_available
                                else [html.P("No budget metrics available")]
                            ),
                        ),
                                html.Div([
                                    html.Label("Kommentarer"),
                                    dcc.Input(
                                        id={"type": "metric-input", "index": "Kommentarer"},
                                        type="text",
                                        placeholder="Lägg till kommentarer om denna månad",
                                        style={"width": "100%", "padding": "8px", "marginBottom": "10px"},
                                    ),
                                ]),
                      
                        
                        html.Button(
                            "Save Entry",
                            id="submit-entry-button",
                            n_clicks=0,
                            style={
                                "padding": "10px 20px",
                                "backgroundColor": "#007bff",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "4px",
                                "cursor": "pointer",
                            },
                        ),
                    ],
                    style={"border": "1px solid #ddd", "padding": "20px", "borderRadius": "4px"},
                ),
                html.Div(
                    id="entry-message",
                    style={"marginTop": "20px", "padding": "10px", "borderRadius": "4px"},
                ),
            ],
            style={"marginTop": "40px", "maxWidth": "600px"},
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


# Callback to handle new entry submission
@app.callback(
    Output("entry-message", "children"),
    Output("entry-message", "style"),
    Input("submit-entry-button", "n_clicks"),
    State("new-month-input", "value"),
    State({"type": "metric-input", "index": ALL}, "value"),
    prevent_initial_call=True,
)
def save_new_entry(n_clicks: int, month_str: str, metric_values: list) -> tuple[str, dict]:
    """Save a new budget entry to the raw CSV file.
    
    Args:
        n_clicks: Number of times the button was clicked
        month_str: Month string in YYYY-MM format
        metric_values: List of values for each metric
        
    Returns:
        Tuple of (message text, style dict for success/error display)
    """
    if not month_str or not metric_values:
        return "Please fill in all fields", {
            "marginTop": "20px",
            "padding": "10px",
            "borderRadius": "4px",
            "backgroundColor": "#f8d7da",
            "color": "#721c24",
        }

    try:
        # Parse the month string
        month_date = pd.to_datetime(month_str)
        
        # Load the raw CSV file
        raw_file_path = Path(__file__).resolve().parent / "data" / "raw" / RAW_BUDGET_FILE
        raw_df = pd.read_csv(raw_file_path)
        
        # Create a new row with the entered values
        new_row_data = {"Månad": month_date.strftime("%Y-%m")}
        
        # Get the metric names from the stored candidate_budget_vars (in the same order as metric_values)
        for i, col in enumerate(candidate_budget_vars):
            if i < len(metric_values) and metric_values[i] is not None:
                new_row_data[col] = float(metric_values[i])
        
        # Append the new row
        new_row_df = pd.DataFrame([new_row_data])
        updated_df = pd.concat([raw_df, new_row_df], ignore_index=True)
        
        # Save back to the CSV file
        updated_df.to_csv(raw_file_path, index=False)
        
        return (
            f"✓ Successfully saved entry for {month_str}. Run analyze_personal_budget.py to update processed data.",
            {
                "marginTop": "20px",
                "padding": "10px",
                "borderRadius": "4px",
                "backgroundColor": "#d4edda",
                "color": "#155724",
            },
        )
    except Exception as e:
        return (
            f"✗ Error saving entry: {str(e)}",
            {
                "marginTop": "20px",
                "padding": "10px",
                "borderRadius": "4px",
                "backgroundColor": "#f8d7da",
                "color": "#721c24",
            },
        )


# Run the Dash application with environment-based configuration
if __name__ == "__main__":
    # Debug mode enables hot reloading when source files change
    # Host and port can be configured via environment variables
    app.run(
        debug=True,
        host=os.getenv("DASH_HOST", "127.0.0.1"),
        port=int(os.getenv("DASH_PORT", "8050")),
        dev_tools_hot_reload=True,
    )
