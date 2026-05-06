from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def time_series_chart(df: pd.DataFrame, y_col: str, chart_type: str) -> go.Figure:
    """Generate a time series chart for the selected variable."""
    if chart_type == "line":
        fig = px.line(df, x="date", y=y_col, markers=True, template="plotly_white")
    elif chart_type == "scatter":
        fig = px.scatter(df, x="date", y=y_col, template="plotly_white")
    else:
        fig = px.histogram(df, x=y_col, nbins=30, template="plotly_white")

    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Date" if chart_type != "histogram" else y_col,
        yaxis_title=y_col if chart_type != "histogram" else "Count",
    )
    return fig


def correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    """Build a heatmap from a correlation matrix."""
    fig = px.imshow(
        corr_df,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
    )
    fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=30, b=20))
    return fig
