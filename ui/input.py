import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

inputs_ui = [
    dbc.Col(
        [
            dbc.Container(
                [
                    dmc.DateTimePicker(
                        valueFormat="DD MMM YYYY hh:mm A",
                        label="Start Date and Time",
                        placeholder="Pick date and time",
                        size="sm",
                        persistence=True,
                        clearable=False,
                        persistence_type="session",
                        id="start-datetime",
                        className="me-3",
                    ),
                    dmc.DateTimePicker(
                        valueFormat="DD MMM YYYY hh:mm A",
                        label="End Date and Time",
                        placeholder="Pick date and time",
                        size="sm",
                        clearable=False,
                        persistence=True,
                        persistence_type="session",
                        id="end-datetime",
                    ),
                ],
                className="d-flex align-items-center justify-content-start ps-0",
            ),
        ],
        width=7,
    ),
    dbc.Col(
        [
            dbc.Label("Analysis Type", className="align-self-start"),
            dmc.SegmentedControl(
                id="analysis-type",
                data=[  # type: ignore
                    {"label": "Generation", "value": "generation"},
                    {"label": "Consumption", "value": "consumption"},
                    {"label": "Summary", "value": "summary"},
                ],
                radius="md",
                value="generation",
                size="md",
                fullWidth=True,
                persistence=True,
                persistence_type="session",
            ),
        ],
        width=3,
    ),
    dbc.Col(
        [
            dmc.RadioGroup(
                children=dmc.Group(
                    [
                        dmc.Radio("Bar Chart", value="bar-chart"),
                        dmc.Radio("Pie Chart", value="pie-chart"),
                    ],
                    my=10,
                    justify="flex-end",
                ),
                value="bar-chart",
                label="Graph Type",
                persistence=True,
                persistence_type="session",
                size="sm",
                className="text-end",
                id="graphs-type",
            ),
        ],
        width=2,
        className="d-flex justify-content-end",
    ),
]
