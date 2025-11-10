from dash import html
import dash_bootstrap_components as dbc

metrics_ui = dbc.Row(
    [
        dbc.Col(
            html.Div(
                [
                    html.Div(
                        "Total Generation",
                        style={
                            "font-size": "0.9rem",
                            "color": "#666",
                            "margin-bottom": "0.5rem",
                        },
                    ),
                    html.Div(
                        style={
                            "font-size": "1.8rem",
                            "font-weight": "bold",
                            "color": "#50C878",
                        },
                        id="total-generation-metric",
                    ),
                ],
                style={
                    "background-color": "#fff",
                    "padding": "0.4rem",
                    "border-radius": "10px",
                    "box-shadow": "0 1px 2px rgba(0,0,0,0.05)",
                    "border-left": "4px solid #50C878",
                    "text-align": "center",
                },
            ),
            width=4,
        ),
        dbc.Col(
            html.Div(
                [
                    html.Div(
                        "Total Consumption",
                        style={
                            "font-size": "0.9rem",
                            "color": "#666",
                            "margin-bottom": "0.5rem",
                        },
                    ),
                    html.Div(
                        style={
                            "font-size": "1.8rem",
                            "font-weight": "bold",
                            "color": "#667eea",
                        },
                        id="total-consumption-metric",
                    ),
                ],
                style={
                    "background-color": "#fff",
                    "padding": "0.4rem",
                    "border-radius": "10px",
                    "box-shadow": "0 1px 2px rgba(0,0,0,0.05)",
                    "border-left": "4px solid #667eea",
                    "text-align": "center",
                },
            ),
            width=4,
        ),
        dbc.Col(
            html.Div(
                [
                    html.Div(
                        "Loss Percentage",
                        style={
                            "font-size": "0.9rem",
                            "color": "#666",
                            "margin-bottom": "0.5rem",
                        },
                    ),
                    html.Div(
                        style={
                            "font-size": "1.8rem",
                            "font-weight": "bold",
                            "color": "#FF6B6B",
                        },
                        id="loss-percentage-metric",
                    ),
                ],
                style={
                    "background-color": "#fff",
                    "padding": "0.4rem",
                    "border-radius": "10px",
                    "box-shadow": "0 1px 2px rgba(0,0,0,0.05)",
                    "border-left": "4px solid #FF6B6B",
                    "text-align": "center",
                },
            ),
            width=4,
        ),
    ],
)
