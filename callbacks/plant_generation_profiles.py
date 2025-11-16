from io import StringIO

import plotly.graph_objects as go
from dash import callback, Output, Input, State
from dash.exceptions import PreventUpdate
import pandas as pd
from .utitls import text_fig


@callback(
    output=dict(
        wholesale_suppliers_select=Output("wholesale-suppliers-select", "value"),
    ),
    inputs=dict(
        all_wholesale_suppliers_checkbox=Input(
            "generation-analysis-all-wholesale-suppliers-checkbox", "checked"
        ),
        global_state=State("global-state-store", "data"),
    ),
)
def update_all_wholesale_suppliers_checkbox(
    all_wholesale_suppliers_checkbox,
    global_state,
):
    if not all_wholesale_suppliers_checkbox:
        raise PreventUpdate
    return dict(wholesale_suppliers_select=global_state["wholesale_suppliers"])


@callback(
    output=dict(
        plant_generation_profiles_chart=Output(
            "plant-generation-profiles-chart", "figure"
        ),
    ),
    inputs=dict(
        generations_json=State("generations-store", "data"),
        wholesale_suppliers=Input("wholesale-suppliers-select", "value"),
        start_datetime=Input("start-datetime", "value"),
        end_datetime=Input("end-datetime", "value"),
        graph_type=Input("plant-generation-profiles-graph-type", "value"),
    ),
)
def update_plant_generation_profiles_chart(
    generations_json,
    wholesale_suppliers,
    start_datetime,
    end_datetime,
    graph_type,
):
    if not generations_json:
        raise PreventUpdate

    if not wholesale_suppliers:
        text_figure = text_fig(
            text="Select wholesale supplier(s)",
            size=24,
            color="orange",
        )
        return dict(plant_generation_profiles_chart=text_figure)

    wholesale_suppliers = (
        [wholesale_suppliers]
        if isinstance(wholesale_suppliers, str)
        else wholesale_suppliers
    )

    generations = pd.read_json(StringIO(generations_json), orient="split")
    generations["Datetime"] = pd.to_datetime(generations["Datetime"], utc=True)

    start_datetime = pd.to_datetime(start_datetime, utc=True)
    end_datetime = pd.to_datetime(end_datetime, utc=True)
    generations = generations[
        (generations["Wholesale_Supplier"].isin(wholesale_suppliers))
        & (generations["Datetime"] >= start_datetime)
        & (generations["Datetime"] <= end_datetime)
    ]
    generations = (
        generations.groupby(["Plant", "Datetime"])["Generation"].sum().reset_index()
    )

    fig = go.Figure()

    plant_totals = (
        generations.groupby("Plant")["Generation"].sum().sort_values(ascending=False)  # type: ignore[arg-type]
    )
    plants = plant_totals.index.tolist()

    for i, plant in enumerate(plants):
        plant_data = generations[generations["Plant"] == plant]
        fig.add_trace(
            go.Scatter(
                x=plant_data["Datetime"],
                y=plant_data["Generation"],
                mode="lines+text",
                name=plant,
                line=dict(width=3, shape="spline"),
                textfont=dict(size=10),
                hoveron="points+fills",
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Time: %{x|%b %d, %Y at %H:%M}<br>"
                    "Generation: %{y:.2f} mWh<extra></extra>"
                ),
                fill=None
                if graph_type == "line-chart"
                else ("tozeroy" if i == 0 else "tonexty"),
                stackgroup="one" if graph_type == "stacked-area-chart" else None,
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
