import dash_mantine_components as dmc
import pandas as pd


def _format_cell(value):
    if isinstance(value, (int, float)):
        return f"{value:,.2f}"
    if pd.api.types.is_scalar(value):
        return str(value)
    return value


def build_table_from_df(df: pd.DataFrame, caption: str):
    head = df.columns.tolist()
    body = [[_format_cell(val) for val in row] for row in df.fillna("").values.tolist()]

    return dmc.TableScrollContainer(
        dmc.Table(
            data={"caption": caption, "head": head, "body": body},
            striped="odd",
            stripedColor="gray.1",  # type: ignore[arg-type]
            withColumnBorders=True,
            highlightOnHover=True,
            withTableBorder=True,
            horizontalSpacing="md",
            verticalSpacing="sm",
            className="summary-table",
        ),
        maxHeight=350,
        type="scrollarea",
        minWidth=500,
    )


def empty_table(columns, caption: str):
    return build_table_from_df(pd.DataFrame(columns=columns), caption)
