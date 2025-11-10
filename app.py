"""
Energy Settlement Dashboard for Ghana Grid Company.

Main application entry point that initializes the Dash app,
defines the layout, and registers all callbacks.
"""

from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

from callbacks import register_callbacks
from ui import upload_section_ui, dashboard_content_ui


external_stylesheets = [
    dbc.themes.FLATLY,
    "assets/styles.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css",
]

app = Dash(
    __name__,
    title="Gridco ESD",
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
    prevent_initial_callbacks=True,
)

app.layout = dbc.Container(
    [
        dcc.Location(id="pathname"),
        html.Div(id="dummy-output", style={"display": "none"}),
        dcc.Store(id="generations-store", storage_type="session"),
        dcc.Store(id="consumptions-store", storage_type="session"),
        dcc.Store(id="plant-consumer-store", storage_type="session"),
        dcc.Store(
            id="global-state-store",
            storage_type="session",
            data={
                "data-name": "No data loaded",
                "metrics": {
                    "total_generation": 0.00,
                    "total_consumption": 0.00,
                    "loss_percentage": 0.00,
                },
                "wholesale_suppliers": [],
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.I(
                            className="fas fa-bolt",
                            style={
                                "margin-right": "1rem",
                                "font-size": "1.5rem",
                                "color": "#667eea",
                            },
                        ),
                        html.H1(
                            "Energy Settlement Dashboard", className="dashboard-title"
                        ),
                    ],
                    style={"display": "flex", "align-items": "center"},
                ),
                html.Div(
                    [
                        html.I(
                            className="fas fa-database",
                            style={"margin-right": "0.5rem", "color": "#667eea"},
                        ),
                        html.Span(
                            id="data-name",
                            style={"color": "#6c757d", "font-size": "0.9rem"},
                        ),
                        dbc.Button(
                            [
                                html.I(
                                    className="fas fa-sync-alt",
                                    style={"margin-right": "0.5rem"},
                                ),
                                "Reload Data",
                            ],
                            id="reload-button",
                            color="primary",
                            outline=True,
                            size="sm",
                            disabled=True,
                            style={"margin-left": "2rem"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "align-items": "center",
                        "margin-top": "0.5rem",
                    },
                ),
            ],
            className="dashboard-header",
        ),
        # Main content sections
        upload_section_ui,
        dashboard_content_ui,
    ],
    fluid=True,
    style={"padding": "2rem"},
)

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
