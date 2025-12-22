import sys
from pathlib import Path

import numpy as np
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# -------------------------------------------------------------------
# PATHS AND IMPORTS
# -------------------------------------------------------------------
sys.path.append(r"C:\Users\diego\project1")
sys.path.append(r"C:\Users\diego\project1\functions")
sys.path.append(r"C:\Users\diego\project1\map_data")

from functions import (
    load_fit_to_df,
    filter_runs_by_city,
    compute_run_stats,
    add_hrv_metrics,
    add_pace_metrics,
    bounding_boxes,
    expand_bbox_with_tolerance,
    parse_tcx
)

# -------------------------------------------------------------------
# LOAD RUNS FROM FIT FILES
# -------------------------------------------------------------------
fit_folder = Path(r"C:\Users\diego\project1\fit_file")
fit_files = list(fit_folder.glob("*.fit"))  # your files are TCX disguised as .fit

runs = []

for file_path in fit_files:
    print("Parsing:", file_path)

    try:
        df = parse_tcx(file_path)  # <-- pass the FILE, not the folder

        if df.empty:
            print("Empty:", file_path.name)
            continue

        df["run_name"] = file_path.stem
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        runs.append({"name": df["run_name"].iloc[0], "df": df})

    except Exception as e:
        print(f"Error parsing {file_path.name}: {e}")



# -------------------------------------------------------------------
# EMPTY FIGURES HELPERS
# -------------------------------------------------------------------
def empty_map_fig():
    return {
        "data": [],
        "layout": {
            "mapbox": {"style": "open-street-map"},
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
        },
    }


def empty_line_fig(title="No data available"):
    return {
        "data": [],
        "layout": {"title": title},
    }


# -------------------------------------------------------------------
# DASH APP
# -------------------------------------------------------------------
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Interactive Run Explorer (FIT + Running Dynamics)"),

        # Country and City selection
        dcc.Dropdown(
            id="country-dropdown",
            options=[{"label": c, "value": c} for c in bounding_boxes.keys()],
            value=list(bounding_boxes.keys())[0],
            clearable=False,
        ),

        dcc.Dropdown(
            id="city-dropdown",
            clearable=False,
            placeholder="Select a city",
        ),

        # Run selection
        dcc.Dropdown(
            id="run-dropdown",
            options=[{"label": r["name"], "value": r["name"]} for r in runs],
            multi=True,
            placeholder="Select runs to compare",
        ),

        # Metric tabs
        dcc.Tabs(
            id="metric-tabs",
            value="hrv",
            children=[
                dcc.Tab(label="HRV", value="hrv"),
                dcc.Tab(label="Pace", value="pace"),
                dcc.Tab(label="Cadence", value="cadence"),
                dcc.Tab(label="Elevation", value="elevation"),
                dcc.Tab(label="Temperature", value="temperature"),
                dcc.Tab(label="Ground Contact Time", value="gct"),
                dcc.Tab(label="Vertical Oscillation", value="vo"),
                dcc.Tab(label="Power", value="power"),
            ],
        ),

        # HRV settings
        html.Div(
            [
                html.Label("HRV method:"),
                dcc.RadioItems(
                    id="hrv-method",
                    options=[
                        {"label": "Standard Deviation", "value": "std"},
                        {"label": "RMSSD", "value": "rmssd"},
                    ],
                    value="std",
                    labelStyle={"display": "inline-block", "margin-right": "15px"},
                ),
            ]
        ),

        html.Div(
            [
                html.Label("HRV window size:"),
                dcc.Slider(
                    id="window-slider",
                    min=5,
                    max=60,
                    step=5,
                    value=10,
                    marks={i: str(i) for i in range(5, 65, 5)},
                ),
            ]
        ),

        html.Hr(),

        # Summary stats
        html.Div(id="summary-stats", style={"display": "flex", "flex-wrap": "wrap"}),

        # Graphs
        dcc.Graph(id="comparison-graph"),
        dcc.Graph(id="map-graph"),
    ]
)


# -------------------------------------------------------------------
# CALLBACK: UPDATE CITY DROPDOWN
# -------------------------------------------------------------------
@app.callback(
    [Output("city-dropdown", "options"), Output("city-dropdown", "value")],
    Input("country-dropdown", "value"),
)
def update_city_dropdown(selected_country):
    cities = list(bounding_boxes[selected_country].keys())
    if not cities:
        return [], None
    return [{"label": c, "value": c} for c in cities], cities[0]


# -------------------------------------------------------------------
# CALLBACK: MAIN UPDATE
# -------------------------------------------------------------------
@app.callback(
    [
        Output("map-graph", "figure"),
        Output("comparison-graph", "figure"),
        Output("summary-stats", "children"),
    ],
    [
        Input("country-dropdown", "value"),
        Input("city-dropdown", "value"),
        Input("run-dropdown", "value"),
        Input("metric-tabs", "value"),
        Input("hrv-method", "value"),
        Input("window-slider", "value"),
    ],
)
def update_graphs(country, city, selected_runs, metric, method, window):
    # If no city yet: empty figs
    if city is None:
        return empty_map_fig(), empty_line_fig(), []

    # Filter runs by city
    filtered_runs = filter_runs_by_city(runs, city, bounding_boxes[country])

    # Filter by selected runs (if user chose any)
    if selected_runs:
        filtered_runs = [r for r in filtered_runs if r["name"] in selected_runs]

    # No runs after filtering
    if not filtered_runs:
        return empty_map_fig(), empty_line_fig(), []

    aligned = []
    stats_cards = []

    for r in filtered_runs:
        df = r["df"].copy()

        # Add HRV & pace metrics
        df = add_hrv_metrics(df, window=window, method=method)
        df = add_pace_metrics(df)

        # Relative index for x-axis
        df["t"] = np.arange(len(df))

        # Summary stats
        stats = compute_run_stats(df)
        stats_cards.append(
            html.Div(
                [
                    html.H4(r["name"]),
                    html.P(f"Distance: {stats['distance_km']:.2f} km"),
                    html.P(f"Avg HR: {stats['avg_hr']:.1f} bpm"),
                    html.P(
                        f"Pace: {stats['avg_pace'] / 60:.2f} min/km"
                        if not np.isnan(stats["avg_pace"])
                        else "Pace: n/a"
                    ),
                ],
                style={
                    "padding": "10px",
                    "border": "1px solid #ccc",
                    "margin": "5px",
                    "width": "220px",
                },
            )
        )

        aligned.append(df)

    df_all = pd.concat(aligned, ignore_index=True)

    # ----------------------------------------------------------------
    # Comparison graph depending on selected metric
    # ----------------------------------------------------------------
    if metric == "hrv":
        fig = px.line(
            df_all,
            x="t",
            y="hrv",
            color="run_name",
            title="HRV Comparison",
        )

    elif metric == "pace":
        fig = px.line(
            df_all,
            x="t",
            y="pace_min_per_km",
            color="run_name",
            title="Pace (min/km) Comparison",
        )

    elif metric == "cadence":
        if "cadence_spm" in df_all.columns:
            fig = px.line(
                df_all,
                x="t",
                y="cadence_spm",
                color="run_name",
                title="Cadence (spm) Comparison",
            )
        else:
            fig = empty_line_fig("Cadence data not available")

    elif metric == "elevation":
        if "elevation_m" in df_all.columns:
            fig = px.line(
                df_all,
                x="t",
                y="elevation_m",
                color="run_name",
                title="Elevation (m) Comparison",
            )
        else:
            fig = empty_line_fig("Elevation data not available")

    elif metric == "temperature":
        if "temperature_c" in df_all.columns:
            fig = px.line(
                df_all,
                x="t",
                y="temperature_c",
                color="run_name",
                title="Temperature (°C) Comparison",
            )
        else:
            fig = empty_line_fig("Temperature data not available")

    elif metric == "gct":
        if "ground_contact_time_ms" in df_all.columns:
            fig = px.line(
                df_all,
                x="t",
                y="ground_contact_time_ms",
                color="run_name",
                title="Ground Contact Time (ms) Comparison",
            )
        else:
            fig = empty_line_fig("Ground contact time data not available")

    elif metric == "vo":
        if "vertical_osc_mm" in df_all.columns:
            fig = px.line(
                df_all,
                x="t",
                y="vertical_osc_mm",
                color="run_name",
                title="Vertical Oscillation (mm) Comparison",
            )
        else:
            fig = empty_line_fig("Vertical oscillation data not available")

    elif metric == "power":
        if "power_w" in df_all.columns:
            fig = px.line(
                df_all,
                x="t",
                y="power_w",
                color="run_name",
                title="Running Power (W) Comparison",
            )
        else:
            fig = empty_line_fig("Power data not available")

    else:
        fig = empty_line_fig()

    # ----------------------------------------------------------------
    # Map figure
    # ----------------------------------------------------------------
    map_fig = px.scatter_mapbox(
        df_all,
        lat="latitude",
        lon="longitude",
        color="run_name",
        mapbox_style="open-street-map",
        zoom=12,
    )

    return map_fig, fig, stats_cards


# -------------------------------------------------------------------
# RUN APP
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)