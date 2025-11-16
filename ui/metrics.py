from dash import html
import dash_bootstrap_components as dbc

metrics_ui = [
    dbc.Col(
        dbc.Container(
            [
                html.Div(
                    "Total Generation",
                    className="metrics-card-title",
                ),
                html.Div(
                    style={"color": "#50C878"},
                    className="metrics-card-value",
                    id="total-generation-metric",
                ),
            ],
            className="metrics-card",
            style={"border-left": "4px solid #50C878"},
        ),
        width=3,
    ),
    dbc.Col(
        dbc.Container(
            [
                html.Div(
                    "Total Consumption",
                    className="metrics-card-title",
                ),
                html.Div(
                    style={"color": "#667eea"},
                    className="metrics-card-value",
                    id="total-consumption-metric",
                ),
            ],
            className="metrics-card",
            style={"border-left": "4px solid #667eea"},
        ),
        width=3,
    ),
    dbc.Col(
        dbc.Container(
            [
                html.Div(
                    "Loss Percentage",
                    className="metrics-card-title",
                ),
                html.Div(
                    className="metrics-card-value",
                    style={"color": "#FF6B6B"},
                    id="loss-percentage-metric",
                ),
            ],
            className="metrics-card",
            style={"border-left": "4px solid #FF6B6B"},
        ),
        width=3,
    ),
]
