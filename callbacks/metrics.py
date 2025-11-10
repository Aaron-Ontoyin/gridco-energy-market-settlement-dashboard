from io import StringIO

from dash import callback, Output, Input, State
import pandas as pd


@callback(
    output=dict(
        total_generation=Output("total-generation-metric", "children"),
        total_consumption=Output("total-consumption-metric", "children"),
        loss_percentage=Output("loss-percentage-metric", "children"),
    ),
    inputs=dict(
        pathname=Input("pathname", "href"),
        start_datetime=Input("datetime-range", "startDate"),
        end_datetime=Input("datetime-range", "endDate"),
        generations_json=State("generations-store", "data"),
        consumptions_json=State("consumptions-store", "data"),
    ),
    prevent_initial_call=True,
)
def update_metrics(
    pathname,
    start_datetime,
    end_datetime,
    generations_json,
    consumptions_json,
):
    generations = pd.read_json(StringIO(generations_json), orient="split")
    consumptions = pd.read_json(StringIO(consumptions_json), orient="split")

    generations["Datetime"] = pd.to_datetime(generations["Datetime"], utc=True)
    consumptions["Datetime"] = pd.to_datetime(consumptions["Datetime"], utc=True)
    end_datetime = pd.to_datetime(end_datetime)
    start_datetime = pd.to_datetime(start_datetime)

    generations = generations[
        (generations["Datetime"] >= start_datetime)
        & (generations["Datetime"] <= end_datetime)
    ]
    consumptions = consumptions[
        (consumptions["Datetime"] >= start_datetime)
        & (consumptions["Datetime"] <= end_datetime)
    ]

    total_generation = generations["Generation"].sum()
    total_generator_consumption = generations["Gen_Consumption"].sum()
    total_actual_consumption = consumptions["Consumption"].sum()
    total_consumption = total_generator_consumption + total_actual_consumption

    loss_pct = 0
    if total_generation > 0:
        loss_pct = ((total_generation - total_consumption) / total_generation) * 100

    return dict(
        total_generation=f"{total_generation:,.2f} mWh",
        total_consumption=f"{total_consumption:,.2f} mWh",
        loss_percentage=f"{loss_pct:,.2f}%",
    )


import_me = True
