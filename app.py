# type: ignore
from datetime import datetime
import base64
from io import StringIO

import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table, State
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

from data_loader import EnergyDataLoader


app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Energy Consumption Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f8f9fa;
            }
            .dashboard-header {
                background: white;
                padding: 1.5rem 2rem;
                border-bottom: 2px solid #e9ecef;
                margin-bottom: 2rem;
            }
            .dashboard-title {
                color: #2c3e50;
                font-size: 2rem;
                font-weight: 600;
                margin: 0;
                text-align: center;
            }
            .filter-card {
                background: white;
                border-radius: 8px;
                padding: 1rem;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
                border: 1px solid #e9ecef;
            }
            .data-card {
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
                border: 1px solid #e9ecef;
            }
            .card-title {
                color: #667eea;
                font-size: 1.3rem;
                font-weight: 600;
                margin-bottom: 1rem;
            }
            .dash-dropdown {
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = dbc.Container(
    [
        # Header
        html.Div(
            [html.H1("Energy Settlement Dashboard", className="dashboard-title")],
            className="dashboard-header",
        ),
        # Data stores (in-memory, expires on browser close)
        dcc.Store(id="generations-store"),
        dcc.Store(id="consumptions-store"),
        dcc.Store(id="plant-consumer-store"),
        # Upload Section
        html.Div(
            id="upload-section",
            children=[
                html.H3("Upload Data File", className="card-title"),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(
                        [
                            html.I(
                                className="fas fa-upload",
                                style={"margin-right": "0.5rem"},
                            ),
                            "Drag and Drop or ",
                            html.A("Select Excel File", style={"color": "#667eea"}),
                        ]
                    ),
                    style={
                        "width": "100%",
                        "height": "80px",
                        "lineHeight": "80px",
                        "borderWidth": "2px",
                        "borderStyle": "dashed",
                        "borderRadius": "10px",
                        "textAlign": "center",
                        "borderColor": "#667eea",
                        "cursor": "pointer",
                        "backgroundColor": "#f8f9fa",
                    },
                    multiple=False,
                ),
                dcc.Loading(
                    id="loading-upload",
                    type="circle",
                    color="#667eea",
                    children=html.Div(
                        id="upload-status",
                        style={"margin-top": "2rem", "text-align": "center"},
                    ),
                ),
            ],
            className="data-card",
        ),
        # Dashboard content (hidden until data is loaded)
        html.Div(
            id="dashboard-content",
            children=[
                # Reload button
                html.Div(
                    html.Button(
                        [
                            html.I(
                                className="fas fa-redo",
                                style={"margin-right": "0.5rem"},
                            ),
                            "Load New File",
                        ],
                        id="reload-button",
                        style={
                            "backgroundColor": "#667eea",
                            "color": "white",
                            "border": "none",
                            "padding": "0.5rem 1.5rem",
                            "borderRadius": "5px",
                            "cursor": "pointer",
                            "fontSize": "0.9rem",
                            "fontWeight": "bold",
                            "marginBottom": "1rem",
                        },
                    ),
                    style={"text-align": "right"},
                ),
                # Overview Section - Date Range Analysis
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Div(
                                                [
                                                    html.Label(
                                                        "Start DateTime:",
                                                        style={
                                                            "color": "#667eea",
                                                            "font-weight": "bold",
                                                            "margin-bottom": "0.5rem",
                                                            "font-size": "0.9rem",
                                                        },
                                                    ),
                                                    dcc.Dropdown(
                                                        id="overview-start-datetime",
                                                        options=[],
                                                        clearable=False,
                                                        placeholder="Select start datetime",
                                                        style={"border-radius": "5px"},
                                                    ),
                                                ],
                                            ),
                                            width=4,
                                        ),
                                        dbc.Col(width=4),
                                        dbc.Col(
                                            html.Div(
                                                [
                                                    html.Label(
                                                        "End DateTime:",
                                                        style={
                                                            "color": "#667eea",
                                                            "font-weight": "bold",
                                                            "margin-bottom": "0.5rem",
                                                            "font-size": "0.9rem",
                                                        },
                                                    ),
                                                    dcc.Dropdown(
                                                        id="overview-end-datetime",
                                                        options=[],
                                                        clearable=False,
                                                        placeholder="Select end datetime",
                                                        style={"border-radius": "5px"},
                                                    ),
                                                ],
                                            ),
                                            width=4,
                                        ),
                                    ],
                                    style={"margin-bottom": "1.5rem"},
                                ),
                                html.Div(id="overview-content"),
                            ],
                            title="System Overview",
                        ),
                    ],
                    start_collapsed=True,
                    style={"margin-bottom": "2rem"},
                ),
                html.H3(
                    "Consumer Detail Analysis",
                    style={
                        "color": "#667eea",
                        "margin-bottom": "1.5rem",
                        "font-weight": "bold",
                    },
                ),
                # Filters
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Label(
                                        "Select Consumer:",
                                        style={
                                            "color": "#667eea",
                                            "font-weight": "bold",
                                            "margin-bottom": "0.5rem",
                                            "font-size": "0.9rem",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="consumer-dropdown",
                                        options=[],
                                        clearable=False,
                                        style={"border-radius": "5px"},
                                    ),
                                ],
                                className="filter-card",
                            ),
                            width=4,
                        ),
                        dbc.Col(width=5),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Label(
                                        "Select Date:",
                                        style={
                                            "color": "#667eea",
                                            "font-weight": "bold",
                                            "margin-bottom": "0.5rem",
                                            "font-size": "0.9rem",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="date-dropdown",
                                        options=[],
                                        clearable=False,
                                        style={"border-radius": "5px"},
                                    ),
                                ],
                                className="filter-card",
                            ),
                            width=3,
                        ),
                    ],
                    style={"margin-bottom": "2rem"},
                ),
                # Consumption Table
                html.Div(
                    [
                        html.H3(
                            "24-Hour Consumption Breakdown", className="card-title"
                        ),
                        html.Div(id="consumption-table"),
                    ],
                    className="data-card",
                ),
                # Chart
                html.Div(
                    [
                        html.H3("Hourly Analysis", className="card-title"),
                        dcc.Graph(id="consumption-chart"),
                    ],
                    className="data-card",
                ),
            ],
            style={"display": "none"},
        ),
    ],
    fluid=True,
    style={"padding": "2rem"},
)


@app.callback(
    [
        Output("generations-store", "data"),
        Output("consumptions-store", "data"),
        Output("plant-consumer-store", "data"),
        Output("upload-status", "children"),
    ],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def upload_file(contents, filename):
    if contents is None:
        return None, None, None, ""

    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        generations, consumptions, plant_consumer = EnergyDataLoader.load_from_excel(
            decoded
        )

        if not EnergyDataLoader.validate_data(
            generations, consumptions, plant_consumer
        ):
            return (
                None,
                None,
                None,
                html.Div(
                    "❌ Invalid data format. Please check the Excel file structure.",
                    style={"color": "red"},
                ),
            )

        generations_json = generations.to_json(date_format="iso", orient="split")
        consumptions_json = consumptions.to_json(date_format="iso", orient="split")
        plant_consumer_json = plant_consumer.to_json(date_format="iso", orient="split")

        return (
            generations_json,
            consumptions_json,
            plant_consumer_json,
            html.Div(
                f"✓ Successfully loaded: {filename}",
                style={"color": "green", "font-weight": "bold"},
            ),
        )
    except Exception as e:
        return (
            None,
            None,
            None,
            html.Div(
                f"❌ Error loading file: {str(e)}",
                style={"color": "red"},
            ),
        )


@app.callback(
    [
        Output("generations-store", "data", allow_duplicate=True),
        Output("consumptions-store", "data", allow_duplicate=True),
        Output("plant-consumer-store", "data", allow_duplicate=True),
        Output("upload-status", "children", allow_duplicate=True),
    ],
    Input("reload-button", "n_clicks"),
    prevent_initial_call=True,
)
def reload_data(n_clicks):
    if n_clicks:
        return None, None, None, ""
    return None, None, None, ""


@app.callback(
    [
        Output("upload-section", "style"),
        Output("dashboard-content", "style"),
        Output("consumer-dropdown", "options"),
        Output("consumer-dropdown", "value"),
        Output("date-dropdown", "options"),
        Output("date-dropdown", "value"),
        Output("overview-start-datetime", "options"),
        Output("overview-start-datetime", "value"),
        Output("overview-end-datetime", "options"),
        Output("overview-end-datetime", "value"),
    ],
    [
        Input("generations-store", "data"),
        Input("plant-consumer-store", "data"),
    ],
)
def update_dropdowns(generations_json, plant_consumer_json):
    if generations_json is None or plant_consumer_json is None:
        return {"display": "block"}, {"display": "none"}, [], None, [], None, [], None, [], None

    try:
        generations = pd.read_json(StringIO(generations_json), orient="split")
        plant_consumer = pd.read_json(StringIO(plant_consumer_json), orient="split")

        consumers = sorted(plant_consumer["Consumer"].unique())
        dates = sorted(generations["Datetime"].dt.date.unique())

        consumer_options = [{"label": c, "value": c} for c in consumers]
        date_options = [{"label": str(d), "value": str(d)} for d in dates]

        # Get all unique datetimes for overview section
        all_datetimes = sorted(generations["Datetime"].unique())
        datetime_options = [
            {"label": dt.strftime("%Y-%m-%d %H:%M"), "value": dt.isoformat()}
            for dt in all_datetimes
        ]

        return (
            {"display": "none"},
            {"display": "block"},
            consumer_options,
            consumers[0] if consumers else None,
            date_options,
            str(dates[0]) if dates else None,
            datetime_options,
            all_datetimes[0].isoformat() if all_datetimes else None,
            datetime_options,
            all_datetimes[-1].isoformat() if all_datetimes else None,
        )
    except Exception:
        return {"display": "block"}, {"display": "none"}, [], None, [], None, [], None, [], None


@app.callback(
    Output("overview-content", "children"),
    [
        Input("overview-start-datetime", "value"),
        Input("overview-end-datetime", "value"),
    ],
    [
        State("generations-store", "data"),
        State("consumptions-store", "data"),
    ],
)
def update_overview(start_datetime, end_datetime, generations_json, consumptions_json):
    if not all([start_datetime, end_datetime, generations_json, consumptions_json]):
        return html.Div(
            "Please select start and end datetime",
            style={"text-align": "center", "padding": "2rem", "color": "#999"},
        )

    try:
        # Parse data
        generations = pd.read_json(StringIO(generations_json), orient="split")
        consumptions = pd.read_json(StringIO(consumptions_json), orient="split")

        # Convert datetime strings to pandas datetime
        start_dt = pd.to_datetime(start_datetime)
        end_dt = pd.to_datetime(end_datetime)

        # Filter data by datetime range
        filtered_generations = generations[
            (generations["Datetime"] >= start_dt) & (generations["Datetime"] <= end_dt)
        ]
        filtered_consumptions = consumptions[
            (consumptions["Datetime"] >= start_dt) & (consumptions["Datetime"] <= end_dt)
        ]

        if len(filtered_generations) == 0 and len(filtered_consumptions) == 0:
            return html.Div(
                "No data available for selected datetime range",
                style={"text-align": "center", "padding": "2rem", "color": "#999"},
            )

        # Aggregate generator data
        generator_summary = (
            filtered_generations.groupby("Plant")
            .agg({"Generation": "sum", "Gen_Consumption": "sum"})
            .reset_index()
        )
        # Convert from Wh to kWh (keep numeric for calculations)
        generator_summary["Total Generation (kWh)"] = (
            generator_summary["Generation"] / 1000
        ).round(2)
        generator_summary["Total Consumption (kWh)"] = (
            generator_summary["Gen_Consumption"] / 1000
        ).round(2)
        generator_summary = generator_summary[
            ["Plant", "Total Generation (kWh)", "Total Consumption (kWh)"]
        ]

        # Aggregate consumer data
        consumer_summary = (
            filtered_consumptions.groupby("Consumer")
            .agg({"Consumption": "sum"})
            .reset_index()
        )
        # Convert from Wh to kWh (keep numeric for calculations)
        consumer_summary["Total Consumption (kWh)"] = (
            consumer_summary["Consumption"] / 1000
        ).round(2)
        consumer_summary = consumer_summary[["Consumer", "Total Consumption (kWh)"]]

        # Format numeric columns with commas for display
        generator_summary_display = generator_summary.copy()
        generator_summary_display["Total Generation (kWh)"] = generator_summary_display[
            "Total Generation (kWh)"
        ].apply(lambda x: f"{x:,.2f}")
        generator_summary_display["Total Consumption (kWh)"] = generator_summary_display[
            "Total Consumption (kWh)"
        ].apply(lambda x: f"{x:,.2f}")

        consumer_summary_display = consumer_summary.copy()
        consumer_summary_display["Total Consumption (kWh)"] = consumer_summary_display[
            "Total Consumption (kWh)"
        ].apply(lambda x: f"{x:,.2f}")

        # Create generator table
        generator_table = dash_table.DataTable(
            data=generator_summary_display.to_dict("records"),
            columns=[{"name": col, "id": col} for col in generator_summary_display.columns],
            page_size=10,
            style_table={"overflowY": "auto"},
            style_cell={
                "textAlign": "center",
                "padding": "0.75rem",
                "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                "fontSize": "0.9rem",
            },
            style_header={
                "backgroundColor": "#667eea",
                "color": "white",
                "fontWeight": "bold",
                "textAlign": "center",
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#f8f9fa",
                }
            ],
        )

        # Create consumer table
        consumer_table = dash_table.DataTable(
            data=consumer_summary_display.to_dict("records"),
            columns=[{"name": col, "id": col} for col in consumer_summary_display.columns],
            page_size=10,
            style_table={"overflowY": "auto"},
            style_cell={
                "textAlign": "center",
                "padding": "0.75rem",
                "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                "fontSize": "0.9rem",
            },
            style_header={
                "backgroundColor": "#667eea",
                "color": "white",
                "fontWeight": "bold",
                "textAlign": "center",
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#f8f9fa",
                }
            ],
        )

        # Calculate summary metrics
        total_generation_kwh = generator_summary["Total Generation (kWh)"].sum()
        total_generator_consumption_kwh = generator_summary["Total Consumption (kWh)"].sum()
        total_actual_consumption_kwh = consumer_summary["Total Consumption (kWh)"].sum()
        total_consumption_kwh = total_generator_consumption_kwh + total_actual_consumption_kwh
        
        # Calculate loss percentage
        loss_pct = 0
        if total_generation_kwh > 0:
            loss_pct = ((total_generation_kwh - total_consumption_kwh) / total_generation_kwh) * 100

        # Prepare time series data for chart
        # Aggregate by datetime for total generation
        gen_timeseries = (
            filtered_generations.groupby("Datetime")["Generation"].sum() / 1000
        )  # Convert to kWh
        
        # Total consumption = actual consumer consumption + generator consumption
        actual_cons_timeseries = (
            filtered_consumptions.groupby("Datetime")["Consumption"].sum() / 1000
        )  # Convert to kWh
        gen_cons_timeseries = (
            filtered_generations.groupby("Datetime")["Gen_Consumption"].sum() / 1000
        )  # Convert to kWh
        
        # Combine actual consumption and generator consumption
        # Use add with fill_value=0 to handle missing timestamps
        total_cons_timeseries = actual_cons_timeseries.add(gen_cons_timeseries, fill_value=0)

        # Create chart
        fig = go.Figure()

        # Add total generation line
        fig.add_trace(
            go.Scatter(
                x=gen_timeseries.index,
                y=gen_timeseries.values,
                mode="lines",
                name="Total Generation",
                line=dict(color="#50C878", width=2),
            )
        )

        # Add total consumption line (actual + generator consumption)
        fig.add_trace(
            go.Scatter(
                x=total_cons_timeseries.index,
                y=total_cons_timeseries.values,
                mode="lines",
                name="Total Consumption",
                line=dict(color="#FF6B6B", width=2),
            )
        )

        fig.update_layout(
            template="plotly_white",
            hovermode="x unified",
            xaxis=dict(
                title="DateTime",
                gridcolor="#e9ecef",
                showgrid=True,
            ),
            yaxis=dict(
                title="Energy (kWh)",
                gridcolor="#e9ecef",
                showgrid=True,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
            ),
            margin=dict(l=40, r=40, t=40, b=40),
        )

        # Return layout with tables and chart
        return html.Div(
            [
                # Summary Metrics Cards
                dbc.Row(
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
                                        f"{total_generation_kwh:,.2f} kWh",
                                        style={
                                            "font-size": "1.8rem",
                                            "font-weight": "bold",
                                            "color": "#50C878",
                                        },
                                    ),
                                ],
                                style={
                                    "background-color": "#fff",
                                    "padding": "1.5rem",
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
                                        f"{total_consumption_kwh:,.2f} kWh",
                                        style={
                                            "font-size": "1.8rem",
                                            "font-weight": "bold",
                                            "color": "#667eea",
                                        },
                                    ),
                                ],
                                style={
                                    "background-color": "#fff",
                                    "padding": "1.5rem",
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
                                        f"{loss_pct:.2f}%",
                                        style={
                                            "font-size": "1.8rem",
                                            "font-weight": "bold",
                                            "color": "#FF6B6B",
                                        },
                                    ),
                                ],
                                style={
                                    "background-color": "#fff",
                                    "padding": "1.5rem",
                                    "border-radius": "10px",
                                    "box-shadow": "0 1px 2px rgba(0,0,0,0.05)",
                                    "border-left": "4px solid #FF6B6B",
                                    "text-align": "center",
                                },
                            ),
                            width=4,
                        ),
                    ],
                    style={"margin-bottom": "2rem"},
                ),
                # Tables Row
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
                                    generator_table,
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
                                    consumer_table,
                                ],
                            ),
                            width=6,
                        ),
                    ],
                    style={"margin-bottom": "2rem"},
                ),
                html.Div(
                    [
                        html.H4(
                            "Time Series Analysis",
                            style={
                                "color": "#667eea",
                                "margin-bottom": "1rem",
                            },
                        ),
                        dcc.Graph(figure=fig),
                    ]
                ),
            ]
        )

    except Exception as e:
        return html.Div(
            f"Error loading overview: {str(e)}",
            style={"color": "red", "text-align": "center", "padding": "2rem"},
        )


@app.callback(
    [
        Output("consumption-table", "children"),
        Output("consumption-chart", "figure"),
    ],
    [
        Input("consumer-dropdown", "value"),
        Input("date-dropdown", "value"),
    ],
    [
        State("generations-store", "data"),
        State("consumptions-store", "data"),
        State("plant-consumer-store", "data"),
    ],
)
def update_dashboard(
    selected_consumer: str,
    selected_date_str: str,
    generations_json,
    consumptions_json,
    plant_consumer_json,
):
    # Return empty if no data or no selections
    if (
        not selected_consumer
        or not selected_date_str
        or not generations_json
        or not consumptions_json
        or not plant_consumer_json
    ):
        empty_msg = html.Div("Please select a consumer and date")
        empty_fig = go.Figure()
        empty_fig.update_layout(template="plotly_white")
        return empty_msg, empty_fig

    try:
        generations = pd.read_json(StringIO(generations_json), orient="split")
        actual_consumptions = pd.read_json(StringIO(consumptions_json), orient="split")
        plant_consumer = pd.read_json(StringIO(plant_consumer_json), orient="split")

        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        consumer_plants = plant_consumer[
            plant_consumer["Consumer"] == selected_consumer
        ]
        customer_actual_consumptions = actual_consumptions[
            (actual_consumptions["Consumer"] == selected_consumer)
            & (actual_consumptions["Datetime"].dt.date == selected_date)
        ]

        date_generations = generations[generations["Datetime"].dt.date == selected_date]
    except Exception:
        empty_msg = html.Div("Error loading data")
        empty_fig = go.Figure()
        empty_fig.update_layout(template="plotly_white")
        return empty_msg, empty_fig

    if len(consumer_plants) > 0:
        hourly_data = []

        for hour in range(24):
            row_data = {"Hour": hour}

            # Calculate consumption and get plant readings for this hour
            total_consumption = 0
            total_generation = 0

            for _, plant_row in consumer_plants.iterrows():
                plant = plant_row["Plant"]
                pct = plant_row["Pct"]

                # Get reading for this plant at this hour
                plant_genearations = date_generations[
                    (date_generations["Plant"] == plant)
                    & (date_generations["Datetime"].dt.hour == hour)
                ]

                if len(plant_genearations) > 0:
                    generation_value_wh = plant_genearations.iloc[0]["Generation"]
                    generation_value = generation_value_wh / 1000
                    consumption = generation_value * pct
                    total_consumption += consumption
                    total_generation += generation_value

                    row_data[f"{plant} Generation (kWh)"] = round(generation_value, 2)
                else:
                    row_data[f"{plant} Generation (kWh)"] = 0

            row_data["Expected Consumption (kWh)"] = round(total_consumption, 2)
            row_data["Total Plants Generation (kWh)"] = round(total_generation, 2)
            hourly_data.append(row_data)

        hourly_df = pd.DataFrame(hourly_data)

        # Add actual consumption by merging on hour
        if len(customer_actual_consumptions) > 0:
            customer_actual_consumptions_with_hour = customer_actual_consumptions.copy()
            customer_actual_consumptions_with_hour["Hour"] = (
                customer_actual_consumptions_with_hour["Datetime"].dt.hour
            )
            # Convert Consumption from Wh to kWh
            customer_actual_consumptions_with_hour["Consumption_kWh"] = (
                customer_actual_consumptions_with_hour["Consumption"] / 1000
            )
            actual_consumption_map = customer_actual_consumptions_with_hour.set_index(
                "Hour"
            )["Consumption_kWh"].to_dict()
            hourly_df["Actual Consumption (kWh)"] = (
                hourly_df["Hour"].map(actual_consumption_map).fillna(0)
            )
        else:
            hourly_df["Actual Consumption (kWh)"] = 0

        # Reorder columns: Hour, Expected Consumption, Actual Consumption, individual plants, Total
        plant_cols = [
            col
            for col in hourly_df.columns
            if col.endswith(" Generation (kWh)") and not col.startswith("Total")
        ]
        column_order = (
            ["Hour", "Expected Consumption (kWh)", "Actual Consumption (kWh)"]
            + sorted(plant_cols)
            + ["Total Plants Generation (kWh)"]
        )
        hourly_df = hourly_df[column_order]

        # Save numeric hours for chart before formatting
        chart_hours = hourly_df["Hour"].copy()
        chart_expected_consumption = hourly_df["Expected Consumption (kWh)"].copy()
        chart_total_generation = hourly_df["Total Plants Generation (kWh)"].copy()
        chart_actual_consumption = hourly_df["Actual Consumption (kWh)"].copy()

        # Format hour for display in table
        hourly_df["Hour"] = hourly_df["Hour"].apply(lambda x: f"{x:02d}:00")

        # Format all numeric columns to 2 decimal places
        numeric_columns = hourly_df.select_dtypes(include=["float64", "int64"]).columns
        for col in numeric_columns:
            hourly_df[col] = hourly_df[col].apply(lambda x: f"{x:.2f}")

        # Transpose the dataframe for horizontal layout
        hourly_df_transposed = hourly_df.set_index("Hour").T
        hourly_df_transposed.insert(0, "Metric", hourly_df_transposed.index)
        hourly_df_transposed = hourly_df_transposed.reset_index(drop=True)

        # Create consumption table
        consumption_table = dash_table.DataTable(
            data=hourly_df_transposed.to_dict("records"),
            columns=[{"name": i, "id": i} for i in hourly_df_transposed.columns],
            style_cell={
                "textAlign": "center",
                "padding": "8px",
                "backgroundColor": "white",
                "color": "#333",
                "border": "1px solid #dee2e6",
                "fontSize": "13px",
                "minWidth": "80px",
            },
            style_header={
                "backgroundColor": "#667eea",
                "fontWeight": "bold",
                "color": "white",
                "border": "1px solid #667eea",
                "fontSize": "13px",
                "whiteSpace": "normal",
                "height": "auto",
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#f8f9fa",
                }
            ],
            style_cell_conditional=[
                {
                    "if": {"column_id": "Metric"},
                    "backgroundColor": "#f8f9fa",
                    "fontWeight": "bold",
                    "textAlign": "left",
                    "minWidth": "180px",
                }
            ],
            style_table={"overflowX": "auto"},
        )

        fig = go.Figure()

        # Use saved numeric hours for plotting
        # Add Actual Consumption as area plot (primary focus)
        fig.add_trace(
            go.Scatter(
                x=chart_hours,
                y=chart_actual_consumption,
                mode="lines",
                name="Actual Consumption",
                line=dict(color="#FF6B6B", width=3, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(255, 107, 107, 0.15)",
            )
        )

        # Add Total Plants Generation line
        fig.add_trace(
            go.Scatter(
                x=chart_hours,
                y=chart_total_generation,
                mode="lines",
                name="Total Plants Generation",
                line=dict(color="#50C878", width=3, shape="spline"),
            )
        )

        # Add Expected Consumption as thinner reference line
        fig.add_trace(
            go.Scatter(
                x=chart_hours,
                y=chart_expected_consumption,
                mode="lines",
                name="Expected Consumption",
                line=dict(color="#4A90E2", width=2, shape="spline", dash="dash"),
            )
        )

        fig.update_layout(
            template="plotly_white",
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                title="Hour of Day",
                gridcolor="#e9ecef",
                showgrid=True,
                tickmode="linear",
                tick0=0,
                dtick=2,
            ),
            yaxis=dict(
                title="Energy (kWh)",
                gridcolor="#e9ecef",
                showgrid=True,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#dee2e6",
                borderwidth=1,
            ),
            hovermode="x unified",
            height=500,
        )

        return consumption_table, fig
    else:
        # No data available
        empty_msg = html.Div(
            "No data available for selected consumer and date",
            style={"color": "#333", "textAlign": "center", "padding": "2rem"},
        )
        empty_fig = go.Figure()
        empty_fig.update_layout(template="plotly_white")
        return empty_msg, empty_fig


if __name__ == "__main__":
    app.run(debug=True, port=8050)
