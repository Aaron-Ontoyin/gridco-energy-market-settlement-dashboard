from dash import html, dcc
import dash_bootstrap_components as dbc

consumption_analysis_ui = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        placeholder="Select Consumer",
                        id="comsumption-analysis-consumer-select",
                        className="mb-3 w-75",
                        clearable=False,
                        persistence=True,
                        persistence_type="session",
                    ),
                ),
                dbc.Col(
                    dcc.DatePickerSingle(
                        id="comsumption-analysis-date-select",
                        date=None,
                        placeholder="Select Date",
                        className="mb-3",
                        display_format="DD MMM YYYY",
                        persistence=True,
                        persistence_type="session",
                        style={"width": "fit-content"},
                    ),
                    className="d-flex justify-content-end",
                ),
            ],
        ),
        dbc.Row(
            [
                html.H3("24-Hour Consumption Breakdown", className="card-title"),
                html.Div(id="consumption-analysis-table"),
            ],
            className="data-card",
        ),
        dbc.Row(
            [
                html.H3("Hourly Analysis", className="card-title"),
                dcc.Graph(
                    id="consumption-analysis-chart", config={"displaylogo": False}
                ),
            ],
            className="data-card",
        ),
    ]
)
