"""
Upload section UI component.
Provides the interface for uploading Excel files containing energy data.
"""
from dash import html, dcc


upload_section_ui = html.Div(
    [
        html.Div(
            [
                html.I(
                    className="fas fa-cloud-upload-alt",
                    style={"margin-right": "0.75rem", "font-size": "1.5rem"},
                ),
                html.H4(
                    "Upload Data (Excel)",
                    className="card-title",
                    style={"margin": "0", "display": "inline-block"},
                ),
            ],
            className="upload-section-title",
        ),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                [
                    html.I(className="fas fa-upload", style={"margin-right": "0.5rem"}),
                    "Drag and Drop or ",
                    html.A("Select Excel File", style={"color": "#667eea"}),
                ]
            ),
            className="upload-section-upload",
            accept=".xlsx,.xls",
            multiple=False,
        ),
        dcc.Loading(
            id="loading-upload",
            type="circle",
            color="#667eea",
            children=html.Div(
                id="upload-status",
                style={"margin-top": "3rem", "text-align": "center"},
            ),
        ),
    ],
    id="upload-section",
    className="data-card",
)
