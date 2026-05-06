from __future__ import annotations

from dash import Dash, Input, Output, dcc, html

from src.analysis import build_correlation_table, compute_summary_metrics
from src.charts import correlation_heatmap, time_series_chart
from src.data_loader import load_or_create_data


df = load_or_create_data()
summary = compute_summary_metrics(df)
corr_table = build_correlation_table(df)

variable_options = [
    {"label": "GDP Growth (%)", "value": "gdp_growth_pct"},
    {"label": "Inflation (%)", "value": "inflation_pct"},
    {"label": "Unemployment (%)", "value": "unemployment_pct"},
    {"label": "Market Index", "value": "market_index"},
    {"label": "Industrial Output", "value": "industrial_output"},
]

chart_type_options = [
    {"label": "Line", "value": "line"},
    {"label": "Scatter", "value": "scatter"},
    {"label": "Histogram", "value": "histogram"},
]

app = Dash(__name__)
app.title = "Scientific and Economic Dashboard"

app.layout = html.Div(
    className="page",
    children=[
        html.Header(
            className="header",
            children=[
                html.H1("Scientific and Economic Analysis Dashboard"),
                html.P("Interactive analysis with Plotly + Dash"),
            ],
        ),
        html.Section(
            className="metrics-grid",
            children=[
                html.Div([
                    html.H3("GDP Growth"),
                    html.P(f"{summary['latest_gdp_growth']:.2f}%")
                ], className="metric-card"),
                html.Div([
                    html.H3("Inflation"),
                    html.P(f"{summary['latest_inflation']:.2f}%")
                ], className="metric-card"),
                html.Div([
                    html.H3("Unemployment"),
                    html.P(f"{summary['latest_unemployment']:.2f}%")
                ], className="metric-card"),
                html.Div([
                    html.H3("Market 12M Change"),
                    html.P(f"{summary['market_index_change_12m']:.2f}%")
                ], className="metric-card"),
            ],
        ),
        html.Section(
            className="controls",
            children=[
                html.Div([
                    html.Label("Variable"),
                    dcc.Dropdown(
                        id="variable-dropdown",
                        options=variable_options,
                        value="gdp_growth_pct",
                        clearable=False,
                    ),
                ]),
                html.Div([
                    html.Label("Chart Type"),
                    dcc.RadioItems(
                        id="chart-type-radio",
                        options=chart_type_options,
                        value="line",
                        inline=True,
                    ),
                ]),
            ],
        ),
        html.Section(
            className="chart-grid",
            children=[
                dcc.Graph(id="main-chart"),
                dcc.Graph(id="correlation-chart", figure=correlation_heatmap(corr_table)),
            ],
        ),
    ],
)


@app.callback(
    Output("main-chart", "figure"),
    Input("variable-dropdown", "value"),
    Input("chart-type-radio", "value"),
)
def update_main_chart(selected_variable: str, selected_chart_type: str):
    return time_series_chart(df, selected_variable, selected_chart_type)


if __name__ == "__main__":
    app.run(debug=True)
