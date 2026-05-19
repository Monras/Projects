"""Visualization utilities for creating Plotly charts.

Provides functions for generating time series, correlation heatmaps,
and budget analysis charts for the dashboard.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def time_series_chart(df: pd.DataFrame, y_col: str, chart_type: str) -> go.Figure:
    """Generate a time series chart for the selected variable.
    
    Args:
        df: DataFrame with date and value columns
        y_col: Column name to plot
        chart_type: Type of chart (line, scatter, or histogram)
        
    Returns:
        Plotly figure object
    """
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
    """Build a heatmap from a correlation matrix.
    
    Args:
        corr_df: Correlation matrix DataFrame
        
    Returns:
        Plotly heatmap figure
    """
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


def budget_timeseries_chart(df: pd.DataFrame, y_col: str, chart_type: str) -> go.Figure:
    """Generate a budget chart for a selected metric over time.
    
    Args:
        df: DataFrame with date column and budget metrics
        y_col: Column name to plot (budget variable)
        chart_type: Type of chart (line, bar, or area)
        
    Returns:
        Plotly figure object with the budget chart
    """
    if chart_type == "line":
        fig = px.line(df, x="date", y=y_col, markers=True, template="plotly_white")
    elif chart_type == "bar":
        fig = px.bar(df, x="date", y=y_col, template="plotly_white")
    else:
        fig = px.area(df, x="date", y=y_col, template="plotly_white")

    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Date",
        yaxis_title=y_col,
    )
    return fig


def income_expense_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """Build a grouped bar chart to compare income vs expenses by month.
    
    Args:
        df: DataFrame with date, Inkomst (income), and Utgifter (expenses) columns
        
    Returns:
        Plotly figure with grouped bar chart, or empty figure if required columns missing
    """
    # Check that required columns exist
    required = {"date", "Inkomst", "Utgifter"}
    if not required.issubset(df.columns):
        return go.Figure()

    # Prepare data in tidy format for grouped bar chart
    tidy = df[["date", "Inkomst", "Utgifter"]].copy()
    melted = tidy.melt(id_vars="date", var_name="series", value_name="value")
    fig = px.bar(
        melted,
        x="date",
        y="value",
        color="series",
        barmode="group",
        template="plotly_white",
        color_discrete_map={"Inkomst": "#0a9396", "Utgifter": "#ee9b00"},
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Date",
        yaxis_title="SEK",
        legend_title_text="",
    )
    return fig
