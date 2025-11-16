from io import StringIO

from dash import callback, Output, Input, State
import pandas as pd
import plotly.graph_objects as go

from .utitls import text_fig


@callback(
    output=dict(
        summary_time_series_chart=Output("summary-time-series-chart", "figure"),
    ),
    inputs=dict(
        generations_json=State("generations-store", "data"),
        consumptions_json=State("consumptions-store", "data"),
        start_dt=Input("start-datetime", "value"),
        end_dt=Input("end-datetime", "value"),
    ),
)
def build_summary_time_series_chart(
    generations_json: str | None,
    consumptions_json: str | None,
    start_dt: str | None,
    end_dt: str | None,
):
    if not generations_json or not consumptions_json or not start_dt or not end_dt:
        return dict(summary_time_series_chart=text_fig("No data available!", size=24))
    generations = pd.read_json(StringIO(generations_json), orient="split")
    consumptions = pd.read_json(StringIO(consumptions_json), orient="split")
    start_datetime = pd.to_datetime(start_dt)
    end_datetime = pd.to_datetime(end_dt)

    filtered_generations = generations[
        (generations["Datetime"] >= start_datetime)
        & (generations["Datetime"] <= end_datetime)
    ]
    filtered_consumptions = consumptions[
        (consumptions["Datetime"] >= start_datetime)
        & (consumptions["Datetime"] <= end_datetime)
    ]

    gen_timeseries = filtered_generations.groupby("Datetime")["Generation"].sum()

    actual_cons_timeseries = filtered_consumptions.groupby("Datetime")[
        "Consumption"
    ].sum()
    gen_cons_timeseries = filtered_generations.groupby("Datetime")[
        "Gen_Consumption"
    ].sum()
    total_cons_timeseries = actual_cons_timeseries.add(
        gen_cons_timeseries, fill_value=0
    )

    loss_pcts = ((gen_timeseries - total_cons_timeseries) / gen_timeseries) * 100

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=gen_timeseries.index,
            y=gen_timeseries.values,
            mode="lines",
            name="Total Generation",
            line=dict(color="green", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=total_cons_timeseries.index,
            y=total_cons_timeseries.values,
            mode="lines",
            name="Total Consumption",
            line=dict(color="blue", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=loss_pcts.index,
            y=loss_pcts.values,
            mode="lines+markers",
            name="Loss (%)",
            line=dict(color="red", width=2),
            yaxis="y2",
            marker=dict(color="red", size=6),
        )
    )

    two_times_max_loss_pct = loss_pcts.max() * 2
    loss_range = [-two_times_max_loss_pct, two_times_max_loss_pct]

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        xaxis=dict(
            title="DateTime",
            gridcolor="#e9ecef",
            showgrid=True,
        ),
        yaxis=dict(
            title="Energy (mWh)",
            gridcolor="#e9ecef",
            showgrid=True,
        ),
        yaxis2=dict(
            title="Loss (%)",
            overlaying="y",
            range=loss_range,
            side="right",
            showgrid=False,
            rangemode="tozero",
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

    return dict(summary_time_series_chart=fig)


import_me = True
