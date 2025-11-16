from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from callbacks.utitls import text_fig


GENERATOR_TABLE_COLUMNS = [
    "Plant",
    "Total Generation (kWh)",
    "Total Consumption (kWh)",
]
CONSUMER_TABLE_COLUMNS = ["Consumer", "Total Consumption (kWh)"]


def _empty_table(head, caption):
    return dmc.TableScrollContainer(
        dmc.Table(
            data={
                "caption": caption,
                "head": head,
                "body": [],
            },
            striped="odd",
            stripedColor="gray.1",  # type: ignore[arg-type]
            withColumnBorders=True,
            highlightOnHover=True,
            withTableBorder=True,
            horizontalSpacing="md",
            verticalSpacing="sm",
            className="summary-table",
        ),
        maxHeight=350,
        type="scrollarea",
        minWidth=500,
    )


generator_table = _empty_table(
    GENERATOR_TABLE_COLUMNS,
    "Generator Summary",
)

consumer_table = _empty_table(
    CONSUMER_TABLE_COLUMNS,
    "Top Consumers",
)


summary_analysis_ui = [
    dbc.Row(
        dcc.Graph(
            figure=text_fig("No data available!", size=24),
            id="summary-time-series-chart",
            config={"displaylogo": False},
        ),
        className="data-card",
    ),
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.H4(
                            "Generator Summary",
                            style={
                                "color": "#667eea",
                                "margin-bottom": "1rem",
                            },
                        ),
                        html.Div(
                            id="generation-summary-table", children=generator_table
                        ),
                    ],
                ),
                width=6,
            ),
            dbc.Col(
                html.Div(
                    [
                        html.H4(
                            "Consumer Summary",
                            style={
                                "color": "#667eea",
                                "margin-bottom": "1rem",
                            },
                        ),
                        html.Div(
                            id="consumption-summary-table", children=consumer_table
                        ),
                    ],
                ),
                width=6,
            ),
        ],
        style={"margin-bottom": "2rem"},
    ),
]
