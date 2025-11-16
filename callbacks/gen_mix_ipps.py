from io import StringIO

import plotly.express as px
import pandas as pd
from dash import callback, Output, Input, State
from dash.exceptions import PreventUpdate

from .utitls import text_fig


@callback(
    output=dict(
        gen_mix_chart=Output("generation-mix-chart", "figure"),
        wholesale_suppliers_chart=Output("wholesale-suppliers-chart", "figure"),
    ),
    inputs=dict(
        generations_json=State("generations-store", "data"),
        start_datetime=Input("start-datetime", "value"),
        end_datetime=Input("end-datetime", "value"),
        graphs_type=Input("graphs-type", "value"),
    ),
)
def update_gen_mix_ipps_chart(
    generations_json, start_datetime, end_datetime, graphs_type
):
    if not generations_json:
        raise PreventUpdate

    if not all([start_datetime, end_datetime]):
        return dict(
            gen_mix_chart=text_fig("Select start and end periods", size=24),
            wholesale_suppliers_chart=text_fig("Select start and end periods", size=24),
        )

    start_datetime = pd.to_datetime(start_datetime)
    end_datetime = pd.to_datetime(end_datetime)
    readable_start_datetime = start_datetime.strftime("%b %d, %y, %H:%M")
    readable_end_datetime = end_datetime.strftime("%b %d, %y, %H:%M")

    gen_mix_data = pd.read_json(StringIO(generations_json), orient="split")
    gen_mix_data["Datetime"] = pd.to_datetime(gen_mix_data["Datetime"])

    if gen_mix_data["Datetime"].dt.tz is not None:
        gen_mix_data["Datetime"] = gen_mix_data["Datetime"].dt.tz_localize(None)
    if start_datetime.tz is not None:
        start_datetime = start_datetime.tz_localize(None)
    if end_datetime.tz is not None:
        end_datetime = end_datetime.tz_localize(None)

    filtered_generations = gen_mix_data[
        (gen_mix_data["Datetime"] >= start_datetime)
        & (gen_mix_data["Datetime"] <= end_datetime)
    ]
    if filtered_generations.empty:
        text_figure = text_fig(
            text=f"No data available for {readable_start_datetime} to {readable_end_datetime}",
            color="orange",
        )
        return dict(gen_mix_chart=text_figure, wholesale_suppliers_chart=text_figure)

    gen_mix_data = filtered_generations.groupby("Gen_Mix")["Generation"].sum()
    wholesale_suppliers_data = filtered_generations.groupby("Wholesale_Supplier")[
        "Generation"
    ].sum()

    if graphs_type == "pie-chart":
        gen_mix = px.pie(
            values=gen_mix_data.values,
            names=gen_mix_data.index,
            title=f"{readable_start_datetime} to {readable_end_datetime}",
        )
        gen_mix.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent}",
            hovertemplate="%{label}<br>%{value:,.2f} mWh<br>%{percent}<extra></extra>",
        )
        gen_mix.update_traces(textposition="inside", textinfo="percent")
        gen_mix.update_layout(showlegend=True)

        wholesale_suppliers = px.pie(
            values=wholesale_suppliers_data.values,
            names=wholesale_suppliers_data.index,
            title=f"{readable_start_datetime} to {readable_end_datetime}",
        )
        wholesale_suppliers.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>%{percent}",
            hovertemplate="%{label}<br>%{value:,.2f} mWh<br>%{percent}<extra></extra>",
        )
        wholesale_suppliers.update_traces(textposition="inside", textinfo="percent")
        wholesale_suppliers.update_layout(showlegend=True)
    else:
        gen_mix = px.bar(
            x=gen_mix_data.index,
            y=gen_mix_data.values,
            title=f"Generation Mix: {readable_start_datetime} to {readable_end_datetime}",
            labels={"x": "Generation Type", "y": "Generation (mWh)"},
        )
        wholesale_suppliers = px.bar(
            x=wholesale_suppliers_data.index,
            y=wholesale_suppliers_data.values,
            title=f"Wholesale Suppliers: {readable_start_datetime} to {readable_end_datetime}",
            labels={"x": "Wholesale Supplier", "y": "Generation (mWh)"},
        )
        gen_mix.update_traces(
            textposition="inside",
            text=[f"{val:,.2f}" for val in gen_mix_data.values],
            hovertemplate="Generation Type: %{x}<br>Generation: %{y:,.2f} mWh<extra></extra>",
        )
        gen_mix.update_layout(showlegend=False)
        wholesale_suppliers.update_traces(
            textposition="inside",
            text=[f"{val:,.2f}" for val in wholesale_suppliers_data.values],
            hovertemplate="Wholesale Supplier: %{x}<br>Generation: %{y:,.2f} mWh<extra></extra>",
        )
        wholesale_suppliers.update_layout(showlegend=False)
    return dict(gen_mix_chart=gen_mix, wholesale_suppliers_chart=wholesale_suppliers)


import_me = True
