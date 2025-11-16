from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

generation_analysis_ui = [
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
                            config={"displaylogo": False},
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
                        html.H3("Generation Mix", className="card-title"),
                        dcc.Graph(
                            id="generation-mix-chart",
                            config={"displaylogo": False},
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
    dbc.Row(
        [
            dbc.Row(
                [
                    dbc.Col(
                        "Plant Generation Profiles", className="card-title", width=3
                    ),
                    dbc.Col(
                        dmc.RadioGroup(
                            children=dmc.Group(
                                [
                                    dmc.Radio("Line Chart", value="line-chart"),
                                    dmc.Radio(
                                        "Stacked Area Chart", value="stacked-area-chart"
                                    ),
                                ],
                                my=10,
                                justify="flex-end",
                            ),
                            value="bar-chart",
                            persistence=True,
                            persistence_type="session",
                            size="sm",
                            id="plant-generation-profiles-graph-type",
                        ),
                        width=3,
                    ),
                    dbc.Col(
                        [
                            dmc.Checkbox(
                                labelPosition="left",
                                label="All",
                                variant="filled",
                                className="me-3",
                                size="md",
                                radius="md",
                                indeterminate=False,
                                id="generation-analysis-all-wholesale-suppliers-checkbox",
                            ),
                            dcc.Dropdown(
                                id="wholesale-suppliers-select",
                                placeholder="Select Wholesale Supplier(s)",
                                style={
                                    "width": "fit-content",
                                    "minWidth": "500px",
                                    "maxWidth": "500px",
                                },
                                multi=True,
                                persistence=True,
                                persistence_type="session",
                            ),
                        ],
                        className="d-flex align-items-center justify-content-end",
                        width=6,
                    ),
                ],
                className="mb-3 d-flex align-items-center justify-content-between",
            ),
            dbc.Row(
                [
                    dcc.Graph(
                        id="plant-generation-profiles-chart",
                        config={"displaylogo": False},
                    )
                ]
            ),
        ],
        className="mb-3",
    ),
]
