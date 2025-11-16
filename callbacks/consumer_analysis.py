import plotly.graph_objects as go
import pandas as pd
from io import StringIO
from datetime import datetime
from dash import callback, Input, Output, State

from .utitls import text_fig
from .build_table import build_table_from_df

EMPTY_TABLE_CONSUMPTION_TABLE = build_table_from_df(
    pd.DataFrame(columns=["Metric"] + [f"{i:02d}:00" for i in range(24)]),  # type: ignore
    "Consumption Analysis",
)


@callback(
    output=dict(
        consumption_analysis_table=Output("consumption-analysis-table", "children"),
        consumption_analysis_chart=Output("consumption-analysis-chart", "figure"),
    ),
    inputs=dict(
        selected_consumer=Input("comsumption-analysis-consumer-select", "value"),
        selected_date_str=Input("comsumption-analysis-date-select", "date"),
        generations_json=State("generations-store", "data"),
        consumptions_json=State("consumptions-store", "data"),
        plant_consumer_json=State("plant-consumer-store", "data"),
    ),
)
def update_dashboard(
    selected_consumer: str,
    selected_date_str: str,
    generations_json: str,
    consumptions_json: str,
    plant_consumer_json: str,
):
    if (
        not selected_consumer
        or not selected_date_str
        or not generations_json
        or not consumptions_json
        or not plant_consumer_json
    ):
        return {
            "consumption_analysis_table": EMPTY_TABLE_CONSUMPTION_TABLE,
            "consumption_analysis_chart": text_fig(
                "Please select a consumer and date", size=24
            ),
        }

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
        return {
            "consumption_analysis_table": EMPTY_TABLE_CONSUMPTION_TABLE,
            "consumption_analysis_chart": text_fig("Error loading data", size=24),
        }

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
                plant_genearations: pd.DataFrame = date_generations[  # type: ignore
                    (date_generations["Plant"] == plant)
                    & (date_generations["Datetime"].dt.hour == hour)  # type: ignore
                ]

                if len(plant_genearations) > 0:
                    generation_value = plant_genearations.iloc[0]["Generation"]
                    consumption = generation_value * pct
                    total_consumption += consumption
                    total_generation += generation_value

                    row_data[f"{plant} Generation (mWh)"] = round(generation_value, 2)
                else:
                    row_data[f"{plant} Generation (mWh)"] = 0

            row_data["Expected Consumption (mWh)"] = round(total_consumption, 2)
            row_data["Total Plants Generation (mWh)"] = round(total_generation, 2)
            hourly_data.append(row_data)

        hourly_df = pd.DataFrame(hourly_data)

        # Add actual consumption by merging on hour
        if len(customer_actual_consumptions) > 0:
            customer_actual_consumptions_with_hour = customer_actual_consumptions.copy()
            customer_actual_consumptions_with_hour["Hour"] = (
                customer_actual_consumptions_with_hour["Datetime"].dt.hour  # type: ignore
            )
            # Convert Consumption from Wh to mWh
            customer_actual_consumptions_with_hour["Consumption_mWh"] = (
                customer_actual_consumptions_with_hour["Consumption"]
            )
            actual_consumption_map = customer_actual_consumptions_with_hour.set_index(
                "Hour"
            )["Consumption_mWh"].to_dict()
            hourly_df["Actual Consumption (mWh)"] = (
                hourly_df["Hour"].map(actual_consumption_map).fillna(0)  # type: ignore
            )
        else:
            hourly_df["Actual Consumption (mWh)"] = 0

        # Reorder columns: Hour, Expected Consumption, Actual Consumption, individual plants, Total
        plant_cols = [
            col
            for col in hourly_df.columns
            if col.endswith(" Generation (mWh)") and not col.startswith("Total")
        ]
        column_order = (
            ["Hour", "Expected Consumption (mWh)", "Actual Consumption (mWh)"]
            + sorted(plant_cols)
            + ["Total Plants Generation (mWh)"]
        )
        hourly_df = hourly_df[column_order]

        # Save numeric hours for chart before formatting
        chart_hours = hourly_df["Hour"].copy()
        chart_expected_consumption = hourly_df["Expected Consumption (mWh)"].copy()
        chart_total_generation = hourly_df["Total Plants Generation (mWh)"].copy()
        chart_actual_consumption = hourly_df["Actual Consumption (mWh)"].copy()

        # Format hour for display in table
        hourly_df["Hour"] = hourly_df["Hour"].apply(lambda x: f"{x:02d}:00")  # type: ignore

        # Transpose the dataframe for horizontal layout
        hourly_df_transposed = hourly_df.set_index("Hour").T
        hourly_df_transposed.insert(0, "Metric", hourly_df_transposed.index)
        hourly_df_transposed = hourly_df_transposed.reset_index(drop=True)

        # Create consumption table
        consumption_table = build_table_from_df(
            hourly_df_transposed, "Consumption Analysis"
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
                title="Energy (mWh)",
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

        return {
            "consumption_analysis_table": consumption_table,
            "consumption_analysis_chart": fig,
        }
    else:
        return {
            "consumption_analysis_table": EMPTY_TABLE_CONSUMPTION_TABLE,
            "consumption_analysis_chart": text_fig(
                "No data available for selected consumer and date", size=24
            ),
        }


import_me = True
