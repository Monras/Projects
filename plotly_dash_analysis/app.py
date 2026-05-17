from __future__ import annotations

import os

from dash import Dash, Input, Output, dcc, html

from src.charts import budget_timeseries_chart, income_expense_comparison_chart
from src.personal_budget_analysis import (
    build_derived_budget_series,
    compute_budget_summary,
    load_personal_budget,
)

budget_available = True
budget_error = ""
budget_chart_df = None
budget_summary: dict[str, float | str] = {}
budget_variable_options: list[dict[str, str]] = []

try:
    budget_monthly = load_personal_budget().reset_index()
    budget_derived = build_derived_budget_series(budget_monthly)
    budget_summary = compute_budget_summary(budget_derived.set_index("date"))
    budget_chart_df = budget_derived

    candidate_budget_vars = [
        "Inkomst",
        "Utgifter",
        "net_cashflow",
        "Sparande",
        "totalt innehav",
        "known_liabilities",
    ]
    budget_variable_options = [
        {"label": col.replace("_", " ").title(), "value": col}
        for col in candidate_budget_vars
        if col in budget_chart_df.columns
    ]
except Exception as exc:  # pragma: no cover - defensive app startup fallback
    budget_available = False
    budget_error = str(exc)

budget_chart_type_options = [
    {"label": "Line", "value": "line"},
    {"label": "Bar", "value": "bar"},
    {"label": "Area", "value": "area"},
]


def _fmt_sek(value: float | str | None) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):,.0f} SEK"


def _fmt_pct(value: float | str | None) -> str:
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


@app.callback(
    Output("budget-main-chart", "figure"),
    Input("budget-variable-dropdown", "value"),
    Input("budget-chart-type-radio", "value"),
)
def update_budget_chart(selected_variable: str | None, selected_chart_type: str):
    if budget_chart_df is None:
        return budget_timeseries_chart(
            load_personal_budget().reset_index(),
            "totalt innehav",
            "line",
        )

    if not selected_variable or selected_variable not in budget_chart_df.columns:
        selected_variable = "totalt innehav"

    return budget_timeseries_chart(budget_chart_df, selected_variable, selected_chart_type)


if __name__ == "__main__":
    app.run(
        debug=os.getenv("DASH_DEBUG", "false").lower() == "true",
        host=os.getenv("DASH_HOST", "0.0.0.0"),
        port=int(os.getenv("DASH_PORT", "8050")),
    )
