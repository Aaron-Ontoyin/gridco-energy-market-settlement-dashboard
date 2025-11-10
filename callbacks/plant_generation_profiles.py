from io import StringIO

import plotly.graph_objects as go
from dash import callback, Output, Input, State
from dash.exceptions import PreventUpdate
import pandas as pd


@callback(
    output=dict(
        plant_generation_profiles_chart=Output(
            "plant-generation-profiles-chart", "figure"
        ),
    ),
    inputs=dict(
        generations_json=State("generations-store", "data"),
        wholesale_suppliers=Input("wholesale-suppliers-select", "value"),
        start_datetime=Input("datetime-range", "startDate"),
        end_datetime=Input("datetime-range", "endDate"),
    ),
)
def update_plant_generation_profiles_chart(
    generations_json,
    wholesale_suppliers,
    start_datetime,
    end_datetime,
):
    if not generations_json or not wholesale_suppliers:
        raise PreventUpdate

    wholesale_suppliers = (
        [wholesale_suppliers]
        if isinstance(wholesale_suppliers, str)
        else wholesale_suppliers
    )

    generations = pd.read_json(StringIO(generations_json), orient="split")
    generations["Datetime"] = pd.to_datetime(generations["Datetime"], utc=True)

    start_datetime = pd.to_datetime(start_datetime)
    end_datetime = pd.to_datetime(end_datetime)
    generations = generations[
        (generations["Wholesale_Supplier"].isin(wholesale_suppliers))
        & (generations["Datetime"] >= start_datetime)
        & (generations["Datetime"] <= end_datetime)
    ]
    generations = (
        generations.groupby(["Plant", "Datetime"])["Generation"].sum().reset_index()
    )

    fig = go.Figure()

    plants = generations["Plant"].unique()

    for plant in plants:
        plant_data = generations[generations["Plant"] == plant]
        fig.add_trace(
            go.Scatter(
                x=plant_data["Datetime"],
                y=plant_data["Generation"],
                mode="lines",
                name=plant,
                line=dict(width=3, shape="spline"),
            )
        )

    fig.update_layout(
        title="Plant Generation Profiles",
        xaxis_title="Datetime",
        yaxis_title="Generation (mWh)",
        showlegend=True,
    )
    return dict(plant_generation_profiles_chart=fig)


import_me = True
