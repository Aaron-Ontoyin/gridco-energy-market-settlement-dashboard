import plotly.graph_objects as go


def text_fig(text: str, color: str = "orange"):
    fig = go.Figure()
    fig.add_annotation(
        text=text,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=14, color=color),
    )
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig
