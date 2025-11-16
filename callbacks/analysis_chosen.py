from dash import callback, Output, Input
from dash.exceptions import PreventUpdate


@callback(
    output=dict(
        generation_analysis_row=Output("generation-analysis-row", "className"),
        consumption_analysis_row=Output("consumption-analysis-row", "className"),
        summary_analysis_row=Output("summary-analysis-row", "className"),
        graphs_type=Output("graphs-type", "display"),
    ),
    inputs=dict(
        analysis_type=Input("analysis-type", "value"),
        pathname=Input("pathname", "href"),
    ),
)
def update_analysis_chosen(analysis_type, pathname):
    if analysis_type == "generation":
        return dict(
            generation_analysis_row="main-analysis-row main-analysis-row-visible",
            consumption_analysis_row="main-analysis-row main-analysis-row-hidden",
            summary_analysis_row="main-analysis-row main-analysis-row-hidden",
            graphs_type="block",
        )
    elif analysis_type == "consumption":
        return dict(
            generation_analysis_row="main-analysis-row main-analysis-row-hidden",
            consumption_analysis_row="main-analysis-row main-analysis-row-visible",
            summary_analysis_row="main-analysis-row main-analysis-row-hidden",
            graphs_type="none",
        )
    elif analysis_type == "summary":
        return dict(
            generation_analysis_row="main-analysis-row main-analysis-row-hidden",
            consumption_analysis_row="main-analysis-row main-analysis-row-hidden",
            summary_analysis_row="main-analysis-row main-analysis-row-visible",
            graphs_type="none",
        )
    else:
        raise PreventUpdate


import_me = True
