"""
Callbacks for handling file uploads and view switching between upload and dashboard.
"""

import base64

from dash import callback, Input, Output, State, no_update, ctx, html, Patch
from dash.exceptions import PreventUpdate
import pandas as pd

from .data_loader import EnergyDataLoader


def df_to_json(df: pd.DataFrame) -> str | None:
    """Convert DataFrame to JSON string for storage."""
    return df.to_json(date_format="iso", orient="split")


@callback(
    output=dict(
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

    Handles two main scenarios:
    1. Reload button clicked: Clear all data and show upload section
    2. Page navigation: Show dashboard if data exists, otherwise show upload section
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

    try:
        content_type, content_string = upload_data_contents.split(",")
        decoded = base64.b64decode(content_string)

        uploaded_data = EnergyDataLoader.load_from_excel(decoded)
        if not EnergyDataLoader.validate_data(uploaded_data):
            global_state["data-name"] = "No data loaded"
            return {
                "pathname": no_update,
                "generations_store_data": None,
                "consumptions_store_data": None,
                "plant_consumer_store_data": None,
                "upload_status": html.Div(
                    "❌ Invalid data format. Please check the Excel file structure.",
                    style={"color": "red"},
                ),
                "global_state": global_state,
                "reload_button_disabled": True,
            }

        global_state["data-name"] = upload_data_filename
        global_state["wholesale_suppliers"] = (
            uploaded_data.generations["Wholesale_Supplier"].unique().tolist()
        )
        return {
            "pathname": "/dashboard",
            "generations_store_data": df_to_json(uploaded_data.generations),
            "consumptions_store_data": df_to_json(uploaded_data.consumptions),
            "plant_consumer_store_data": df_to_json(uploaded_data.plant_consumer),
            "upload_status": html.Div(
                f"✓ Successfully loaded: {upload_data_filename}",
                style={"color": "green", "font-weight": "bold"},
            ),
            "global_state": global_state,
            "reload_button_disabled": False,
        }

    except Exception as e:
        global_state["data-name"] = "No data loaded"
        return {
            "pathname": no_update,
            "generations_store_data": None,
            "consumptions_store_data": None,
            "plant_consumer_store_data": None,
            "upload_status": html.Div(
                f"❌ Error loading file: {str(e)}",
                style={"color": "red"},
            ),
            "global_state": global_state,
            "reload_button_disabled": True,
        }


import_me = True
