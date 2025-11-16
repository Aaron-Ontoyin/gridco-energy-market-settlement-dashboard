"""
Callbacks for handling file uploads and view switching between upload and dashboard.
"""

import base64
from io import StringIO

from dash import callback, Input, Output, State, no_update, ctx, html, Patch
from dash.exceptions import PreventUpdate
import pandas as pd

from .data_loader import EnergyDataLoader
from .build_table import empty_table, build_table_from_df


def df_to_json(df: pd.DataFrame) -> str | None:
    """Convert DataFrame to JSON string for storage."""
    return df.to_json(date_format="iso", orient="split")


GENERATOR_TABLE_COLUMNS = [
    "Plant",
    "Total Generation (mWh)",
    "Total Consumption (mWh)",
]
CONSUMER_TABLE_COLUMNS = ["Consumer", "Total Consumption (mWh)"]


def _json_to_df(json_str: str | None) -> pd.DataFrame | None:
    if not json_str:
        return None
    try:
        return pd.read_json(StringIO(json_str), orient="split")
    except ValueError:
        return None


def build_generation_summary_table(generations: pd.DataFrame | None):
    if generations is None or generations.empty:
        return empty_table(
            columns=GENERATOR_TABLE_COLUMNS, caption="Generation Summary"
        )

    available_cols = [
        col for col in ["Generation", "Gen_Consumption"] if col in generations.columns
    ]
    if not available_cols:
        return empty_table(
            columns=GENERATOR_TABLE_COLUMNS, caption="Generation Summary"
        )

    summary_df = (
        generations.groupby("Plant")[available_cols]
        .sum()
        .reset_index()
        .rename(
            columns={
                "Generation": "Total Generation (mWh)",
                "Gen_Consumption": "Total Consumption (mWh)",
            }
        )
        .sort_values(by="Total Generation (mWh)", ascending=False)
    )

    return build_table_from_df(summary_df, "Generation Summary")


def build_consumption_summary_table(consumptions: pd.DataFrame | None):
    if consumptions is None or consumptions.empty:
        return empty_table(
            columns=CONSUMER_TABLE_COLUMNS, caption="Consumption Summary"
        )

    if "Consumption" not in consumptions.columns:
        consumptions = consumptions.rename(columns={"Value": "Consumption"})

    if "Consumption" not in consumptions.columns:
        return empty_table(
            columns=CONSUMER_TABLE_COLUMNS, caption="Consumption Summary"
        )

    summary_df = (
        consumptions.groupby("Consumer")["Consumption"]
        .sum()
        .reset_index()
        .rename(columns={"Consumption": "Total Consumption (mWh)"})
        .sort_values(by="Total Consumption (mWh)", ascending=False)
    )

    return build_table_from_df(summary_df, "Consumption Summary")


@callback(
    output=dict(
        data_name=Output("data-name", "children"),
        upload_section_class=Output("upload-section", "className"),
        dashboard_content_class=Output("dashboard-content", "className"),
        uploaded_data=dict(
            generations_data=Output("generations-store", "data"),
            consumptions_data=Output("consumptions-store", "data"),
            plant_consumer_data=Output("plant-consumer-store", "data"),
        ),
        reload_button_disabled=Output("reload-button", "disabled"),
        upload_status=Output("upload-status", "children"),
        uploaded_data_contents=Output("upload-data", "contents"),
        global_state_out=Output("global-state-store", "data"),
        wholesale_suppliers_options=Output("wholesale-suppliers-select", "options"),
        generation_summary_table=Output("generation-summary-table", "children"),
        consumption_summary_table=Output("consumption-summary-table", "children"),
        consumers_options=Output("comsumption-analysis-consumer-select", "options"),
        analysis_dates=dict(
            consumption_min=Output(
                "comsumption-analysis-date-select", "min_date_allowed"
            ),
            consumption_max=Output(
                "comsumption-analysis-date-select", "max_date_allowed"
            ),
            generation_start_min=Output("start-datetime", "minDate"),
            generation_start_max=Output("start-datetime", "maxDate"),
            generation_end_min=Output("end-datetime", "minDate"),
            generation_end_max=Output("end-datetime", "maxDate"),
        ),
    ),
    inputs=dict(
        pathname=Input("pathname", "href"),
        reload_button=Input("reload-button", "n_clicks"),
        uploaded_data=dict(
            generations_data=State("generations-store", "data"),
            consumptions_data=State("consumptions-store", "data"),
            plant_consumer_data=State("plant-consumer-store", "data"),
        ),
        global_state_in=State("global-state-store", "data"),
    ),
)
def show_upload_or_dashboard(pathname, reload_button, uploaded_data, global_state_in):
    """
    Control visibility of upload section vs dashboard based on data availability.
    """
    global_state_in["data-name"] = global_state_in["data-name"] or "No data loaded"

    output = {
        "upload_section_class": "",
        "dashboard_content_class": "",
        "uploaded_data": {
            "generations_data": no_update,
            "consumptions_data": no_update,
            "plant_consumer_data": no_update,
        },
        "reload_button_disabled": True,
        "upload_status": no_update,
        "uploaded_data_contents": None,
        "global_state_out": global_state_in,
        "wholesale_suppliers_options": global_state_in["wholesale_suppliers"],
        "generation_summary_table": empty_table(
            columns=GENERATOR_TABLE_COLUMNS, caption="Generation Summary"
        ),
        "consumption_summary_table": empty_table(
            columns=CONSUMER_TABLE_COLUMNS, caption="Consumption Summary"
        ),
        "consumers_options": no_update,
        "analysis_dates": {
            "consumption_min": no_update,
            "consumption_max": no_update,
            "generation_start_min": no_update,
            "generation_start_max": no_update,
            "generation_end_min": no_update,
            "generation_end_max": no_update,
        },
        "data_name": global_state_in["data-name"],
    }

    # Handle reload button click - clear all data and return to upload view
    if ctx.triggered_id == "reload-button":
        output["dashboard_content_class"] = "hidden"
        output["uploaded_data"]["generations_data"] = None
        output["uploaded_data"]["consumptions_data"] = None
        output["uploaded_data"]["plant_consumer_data"] = None
        output["upload_status"] = ""

    # Show upload section if all data is not loaded
    elif not all(uploaded_data.values()):
        output["dashboard_content_class"] = "hidden"

    # Show dashboard if data exists
    else:
        output["upload_section_class"] = "hidden"
        output["reload_button_disabled"] = False
        generations_df = _json_to_df(uploaded_data["generations_data"])
        consumptions_df = _json_to_df(uploaded_data["consumptions_data"])
        output["generation_summary_table"] = build_generation_summary_table(
            generations_df
        )
        output["consumption_summary_table"] = build_consumption_summary_table(
            consumptions_df
        )

    if uploaded_data["generations_data"] and uploaded_data["consumptions_data"]:
        generations_df = _json_to_df(uploaded_data["generations_data"])
        consumptions_df = _json_to_df(uploaded_data["consumptions_data"])
        consumers = consumptions_df["Consumer"].unique().tolist()  # type: ignore
        gen_min_datetime = generations_df["Datetime"].min()  # type: ignore
        gen_max_datetime = generations_df["Datetime"].max()  # type: ignore
        cons_min_datetime = consumptions_df["Datetime"].min()  # type: ignore
        cons_max_datetime = consumptions_df["Datetime"].max()  # type: ignore
        min_datetime = min(gen_min_datetime, cons_min_datetime)
        max_datetime = max(gen_max_datetime, cons_max_datetime)

        output["analysis_dates"] = {
            "consumption_min": min_datetime,
            "consumption_max": max_datetime,
            "generation_start_min": min_datetime,
            "generation_start_max": max_datetime,
            "generation_end_min": min_datetime,
            "generation_end_max": max_datetime,
        }
        output["consumers_options"] = consumers

    return output


@callback(
    output=dict(
        pathname=Output("pathname", "href", allow_duplicate=True),
        generations_store_data=Output(
            "generations-store", "data", allow_duplicate=True
        ),
        consumptions_store_data=Output(
            "consumptions-store", "data", allow_duplicate=True
        ),
        plant_consumer_store_data=Output(
            "plant-consumer-store", "data", allow_duplicate=True
        ),
        upload_status=Output("upload-status", "children", allow_duplicate=True),
        global_state=Output("global-state-store", "data", allow_duplicate=True),
        reload_button_disabled=Output(
            "reload-button", "disabled", allow_duplicate=True
        ),
    ),
    inputs=dict(
        upload_data_contents=Input("upload-data", "contents"),
        upload_data_filename=State("upload-data", "filename"),
    ),
    running=[(Output("upload-data", "disabled"), True, False)],
    prevent_initial_call=True,
)
def upload_file(upload_data_contents, upload_data_filename):
    """
    Handle file upload, validation, and data processing.

    Processes uploaded Excel file containing energy settlement data,
    validates it, and stores it in session storage. On success, navigates
    to the dashboard view.

    Returns:
        dict: Contains processed data, upload status, and navigation state
    """
    if upload_data_contents is None:
        raise PreventUpdate
    global_state = Patch()

    output = {
        "pathname": no_update,
        "generations_store_data": None,
        "consumptions_store_data": None,
        "plant_consumer_store_data": None,
        "upload_status": no_update,
        "global_state": global_state,
        "reload_button_disabled": True,
    }

    try:
        content_type, content_string = upload_data_contents.split(",")
        decoded = base64.b64decode(content_string)

        uploaded_data = EnergyDataLoader.load_from_excel(decoded)
        if not EnergyDataLoader.validate_data(uploaded_data):
            global_state["data-name"] = "No data loaded"
            output["upload_status"] = html.Div(
                "❌ Invalid data format. Please check the Excel file structure.",
                style={"color": "red"},
            )
            return output

        global_state["data-name"] = upload_data_filename
        global_state["wholesale_suppliers"] = (
            uploaded_data.generations["Wholesale_Supplier"].unique().tolist()
        )

        output["pathname"] = "/dashboard"
        output["generations_store_data"] = df_to_json(uploaded_data.generations)
        output["consumptions_store_data"] = df_to_json(uploaded_data.consumptions)
        output["plant_consumer_store_data"] = df_to_json(uploaded_data.plant_consumer)
        output["upload_status"] = html.Div(
            f"✓ Successfully loaded: {upload_data_filename}",
            style={"color": "green", "font-weight": "bold"},
        )
        output["reload_button_disabled"] = False
    except Exception as e:
        global_state["data-name"] = "No data loaded"
        output["upload_status"] = html.Div(
            f"❌ Error loading file: {str(e)}",
            style={"color": "red"},
        )

    return output


import_me = True
