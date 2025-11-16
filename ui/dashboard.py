"""
Dashboard content UI component.
Contains the main analytics and visualization interface.
"""

from dash import html
import dash_bootstrap_components as dbc

from .metrics import metrics_ui
from .input import inputs_ui
from .generation_analysis import generation_analysis_ui
from .consumption_analysis import consumption_analysis_ui
from .summary_analysis import summary_analysis_ui

dashboard_content_ui = html.Div(
    [
        dbc.Row(inputs_ui, className="mb-3"),
        dbc.Row(metrics_ui, className="data-card mx-1 justify-content-between"),
        dbc.Row(
            generation_analysis_ui,
            id="generation-analysis-row",
            className="main-analysis-row main-analysis-row-visible",
        ),
        dbc.Row(
            consumption_analysis_ui,
            id="consumption-analysis-row",
            className="main-analysis-row main-analysis-row-hidden",
        ),
        dbc.Row(
            summary_analysis_ui,
            id="summary-analysis-row",
            className="main-analysis-row main-analysis-row-hidden",
        ),
    ],
    className="hidden",
    id="dashboard-content",
)
