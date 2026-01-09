"""
Main Dash application for running data visualization.

Provides interactive dashboard with:
- HRV, pace, cadence, elevation metrics
- Running dynamics (ground contact time, vertical oscillation, power)
- Geographic filtering by city
- Map visualization of routes
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Project imports
from running_analyzer.parsers import parse_tcx
from running_analyzer.metrics import add_hrv_metrics, add_pace_metrics, compute_run_stats
from running_analyzer.geo import bounding_boxes, filter_runs_by_city
from running_analyzer.utils import format_run_name, format_pace, format_distance
from running_analyzer.geo.detectors import detect_or_create_city
from running_analyzer.geo.country_finder import get_country
from running_analyzer.geo.cache import load_auto_cities




# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurable fit folder via environment variable
DEFAULT_DATA_FOLDER = Path(__file__).parent.parent.parent / "data" / "fit_files"
FIT_FOLDER = Path(os.environ.get("RUN_FIT_FOLDER", DEFAULT_DATA_FOLDER))


def load_all_runs(fit_folder: Path) -> List[Dict[str, object]]:
    """
    Load all .fit (or .tcx) files from the fit_folder.
    Returns a list of dicts: {"name": run_name, "df": dataframe}.
    """
    runs: List[Dict[str, object]] = []
    if not fit_folder.exists():
        logger.warning("Fit folder does not exist: %s", fit_folder)
        return runs

    # Process both .fit and .tcx if present
    for ext in ("*.fit", "*.tcx"):
        for file_path in sorted(fit_folder.glob(ext)):
            logger.info("Parsing %s", file_path)
            try:
                df = parse_tcx(file_path)
            except Exception as exc:
                logger.exception("Failed to parse %s: %s", file_path, exc)
                continue

            if df is None or df.empty:
                logger.info("Empty dataframe for %s", file_path.name)
                continue

            df = df.copy()
            # Format run name to be more readable
            readable_name = format_run_name(file_path.stem)
            df["run_name"] = readable_name
            # safe parse timestamp
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            else:
                df["timestamp"] = pd.NaT

            runs.append({"name": readable_name, "df": df})

    logger.info("Loaded %d runs", len(runs))
    return runs


def empty_map_fig():
    """Return empty map figure."""
    return {
        "data": [],
        "layout": {
            "mapbox": {"style": "open-street-map"},
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
        },
    }


def empty_line_fig(title: str = "No data available"):
    """Return empty line figure with title."""
    return {
        "data": [],
        "layout": {"title": title},
    }


def create_layout(runs: List[Dict[str, object]]):
    """Create Dash application layout."""

    # Build country list dynamically from detected runs
    detected_countries = sorted({r["country"] for r in runs})

    return html.Div(
        [
            html.H1("Interactive Run Explorer (FIT + Running Dynamics)"),

            # Country dropdown (dynamic)
            dcc.Dropdown(
                id="country-dropdown",
                options=[{"label": c, "value": c} for c in detected_countries],
                value=detected_countries[0] if detected_countries else None,
                clearable=False,
            ),

            # City dropdown (dynamic)
            dcc.Dropdown(
                id="city-dropdown",
                clearable=False,
                placeholder="Select a city",
            ),

            # Run selector
            dcc.Dropdown(
                id="run-dropdown",
                options=[{"label": r["name"], "value": r["name"]} for r in runs],
                multi=True,
                placeholder="Select runs to compare",
            ),

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
            html.Div(id="summary-stats", style={"display": "flex", "flex-wrap": "wrap"}),
            dcc.Graph(id="comparison-graph"),
            dcc.Graph(id="map-graph"),
        ]
    )

def create_app(runs: List[Dict[str, object]]):
    """Create and configure Dash app."""
    app = dash.Dash(__name__)
    app.layout = create_layout(runs)

    # --- UPDATED CITY DROPDOWN CALLBACK ---
    @app.callback(
        [Output("city-dropdown", "options"), Output("city-dropdown", "value")],
        Input("country-dropdown", "value"),
    )
    def update_city_dropdown(selected_country: Optional[str]):
        if not selected_country:
            return [], None

        # Build city list dynamically from detected runs
        cities = sorted({r["city"] for r in runs if r["country"] == selected_country})

        if not cities:
            return [], None

        return [{"label": c, "value": c} for c in cities], cities[0]

    # --- YOUR EXISTING GRAPH CALLBACK REMAINS UNCHANGED ---
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
        # If no city is selected, return empty figures
        if city is None:
            return empty_map_fig(), empty_line_fig(), []

        # Filter runs by detected country + city
        filtered_runs = [
            r for r in runs
            if r.get("country") == country and r.get("city") == city
        ]

        # Filter by selected runs (if the user selected any)
        if selected_runs:
            filtered_runs = [r for r in filtered_runs if r["name"] in selected_runs]

        if not filtered_runs:
            return empty_map_fig(), empty_line_fig(), []

        aligned = []
        stats_cards = []

        for r in filtered_runs:
            df = r["df"].copy()

            # Add HRV & pace metrics
            try:
                df = add_hrv_metrics(df, window=window, method=method)
            except Exception:
                logger.exception("add_hrv_metrics failed for %s", r["name"])

            try:
                df = add_pace_metrics(df)
            except Exception:
                logger.exception("add_pace_metrics failed for %s", r["name"])

            # Relative index for x-axis
            df["t"] = np.arange(len(df))

            # Summary stats
            try:
                stats = compute_run_stats(df)
            except Exception:
                logger.exception("compute_run_stats failed for %s", r["name"])
                stats = {
                    "distance_km": float("nan"),
                    "avg_hr": float("nan"),
                    "avg_pace": float("nan")
                }

            # Stats card
            stats_cards.append(
                html.Div(
                    [
                        html.H4(r["name"]),
                        html.P(f"Distance: {format_distance(stats.get('distance_km', 0) * 1000)}"),
                        html.P(f"Avg HR: {stats.get('avg_hr', 0):.1f} bpm"),
                        html.P(f"Pace: {format_pace(stats.get('avg_pace', 0))}"),
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

        # Combine all runs
        df_all = pd.concat(aligned, ignore_index=True)

        # Build comparison figure depending on selected metric
        if metric == "hrv":
            fig = px.line(df_all, x="t", y="hrv", color="run_name", title="HRV Comparison")
        elif metric == "pace":
            fig = px.line(df_all, x="t", y="pace_min_per_km", color="run_name", title="Pace (min/km) Comparison")
        elif metric == "cadence":
            fig = px.line(df_all, x="t", y="cadence_spm", color="run_name", title="Cadence (spm) Comparison") \
                if "cadence_spm" in df_all.columns else empty_line_fig("Cadence data not available")
        elif metric == "elevation":
            fig = px.line(df_all, x="t", y="elevation_m", color="run_name", title="Elevation (m) Comparison") \
                if "elevation_m" in df_all.columns else empty_line_fig("Elevation data not available")
        elif metric == "temperature":
            fig = px.line(df_all, x="t", y="temperature_c", color="run_name", title="Temperature (°C) Comparison") \
                if "temperature_c" in df_all.columns else empty_line_fig("Temperature data not available")
        elif metric == "gct":
            fig = px.line(df_all, x="t", y="ground_contact_time_ms", color="run_name", title="Ground Contact Time (ms) Comparison") \
                if "ground_contact_time_ms" in df_all.columns else empty_line_fig("Ground contact time data not available")
        elif metric == "vo":
            fig = px.line(df_all, x="t", y="vertical_osc_mm", color="run_name", title="Vertical Oscillation (mm) Comparison") \
                if "vertical_osc_mm" in df_all.columns else empty_line_fig("Vertical oscillation data not available")
        elif metric == "power":
            fig = px.line(df_all, x="t", y="power_w", color="run_name", title="Running Power (W) Comparison") \
                if "power_w" in df_all.columns else empty_line_fig("Power data not available")
        else:
            fig = empty_line_fig()

        # Map figure

        if {"latitude", "longitude"}.issubset(df_all.columns):
            map_fig = px.scatter_mapbox(
                df_all,
                lat="latitude",
                lon="longitude",
                color="run_name",
                mapbox_style="open-street-map",
                zoom=12,
            )
        else:
            map_fig = empty_map_fig()

        return map_fig, fig, stats_cards


    return app


def main():
    """Main entry point."""
    # Get debug mode from environment
    debug_mode = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
    
    runs = load_all_runs(FIT_FOLDER)
    app = create_app(runs)
    app.run(debug=debug_mode)


if __name__ == "__main__":
    main()
