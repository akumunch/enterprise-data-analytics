import os
import uuid
import matplotlib
matplotlib.use("Agg")  # no display needed, just save to file
import matplotlib.pyplot as plt
import pandas as pd
from langchain_core.tools import tool


from tools.sql_tools import _get_connection, validate_select_only

CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True) #to gen charts with matplotlib

@tool
def generate_chart(sql_query: str, chart_type: str, x_column: str, y_column: str, title: str) -> str:
    """
    Run a SELECT query and save a line or bar chart as a PNG file.
    chart_type must be 'line' or 'bar'. x_column and y_column must match
    column names returned by the query. Returns the saved file path.
    """
    print("[DEBUG] generate_chart called")
    error = validate_select_only(sql_query)
    if error:
        return error

    try:
        with _get_connection() as conn:
            df = pd.read_sql(sql_query.strip().rstrip(";"), conn) #loads query results straight into a DataFrame instead of manually looping rows
    except Exception as e:
        return f"Database error: {e}"

    if df.empty:
        return "Error: Query returned no rows. Cannot generate a chart from empty data."

    df[y_column] = df[y_column].astype(float)

    if x_column not in df.columns or y_column not in df.columns:
        return f"Error: columns must be one of {list(df.columns)}"

    fig, ax = plt.subplots(figsize=(8, 5))
    if chart_type == "bar":
        ax.bar(df[x_column].astype(str), df[y_column])
    elif chart_type == "line":
        ax.plot(df[x_column].astype(str), df[y_column], marker="o")
    else:
        return "Error: chart_type must be 'line' or 'bar'."

    ax.set_title(title)
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    filename = f"{CHARTS_DIR}/{uuid.uuid4().hex[:8]}.png"
    plt.savefig(filename)
    plt.close(fig)

    return f"Chart saved to {filename}"