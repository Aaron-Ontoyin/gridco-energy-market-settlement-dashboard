"""
Dashboard content UI component.
Contains the main analytics and visualization interface.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_datetimepicker

from .metrics import metrics_ui

dashboard_content_ui = html.Div(
    [
        html.Div(
            [
                dash_datetimepicker.DashDatetimepicker(id="datetime-range", utc=True),
                dbc.Select(
                    id="graphs-type",
                    options=[
                        {"label": "Bar Chart", "value": "bar-chart"},
                        {"label": "Pie Chart", "value": "pie-chart"},
                    ],
                    value="bar-chart",
                    style={"width": "fit-content"},
                ),
            ],
            className="mb-3 d-flex align-items-center justify-content-between",
        ),
        html.Div(metrics_ui, className="data-card"),
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.H3(
                                            "Wholesale Suppliers",
                                            className="card-title",
                                        ),
                                        dcc.Graph(
                                            id="wholesale-suppliers-chart",
                                            config={"displayModeBar": False},
                                        ),
                                    ],
                                    className="data-card",
                                ),
                                lg=6,
                                md=12,
                            ),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.H3(
                                            "Generation Mix", className="card-title"
                                        ),
                                        dcc.Graph(
                                            id="generation-mix-chart",
                                            config={"displayModeBar": False},
                                        ),
                                    ],
                                    className="data-card",
                                ),
                                lg=6,
                                md=12,
                            ),
                        ],
                        className="mb-3",
                    ),
                    title="Generation Summary",
                    className="accordion-item",
                ),
                dbc.AccordionItem(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "Plant Generation Profiles",
                                        className="card-title",
                                    ),
                                    dcc.Dropdown(
                                        id="wholesale-suppliers-select",
                                        placeholder="Select Wholesale Supplier(s)",
                                        style={
                                            "width": "fit-content",
                                            "minWidth": "300px",
                                        },
                                        multi=True,
                                        persistence=True,
                                        persistence_type="session",
                                    ),
                                ],
                                className="mb-3 d-flex align-items-center justify-content-between",
                            ),
                            dcc.Graph(
                                id="plant-generation-profiles-chart",
                                config={"displayModeBar": False},
                            ),
                        ],
                        className="mb-3",
                    ),
                    title="Plant Generation Profiles",
                    className="accordion-item",
                ),
            ],
            start_collapsed=True,
            className="mb-3",
        ),
    ],
    className="hidden",
    id="dashboard-content",
)
