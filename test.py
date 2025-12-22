import sys
# Add parent folder to Python path
sys.path.append(r"C:\Users\diego\project1\map_test")
#importing data from other codes
from map_test import df_selected #df_selected from map_test
from map_test import bounding_boxes  # your bounding box definitions

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

# Helper: add HRV metrics
def add_hrv_metrics(df, window=10, method="std"):
    if method == "std":
        df['hrv'] = df['hr_bpm'].rolling(window=window).std()
    elif method == "rmssd":
        diffs = df['hr_bpm'].diff()
        df['hrv'] = np.sqrt((diffs**2).rolling(window=window).mean())
    return df

# Helper: filter by bounding box
def filter_by_bbox(df, bbox):
    return df[
        (df['latitude'] >= bbox['lat_min']) &
        (df['latitude'] <= bbox['lat_max']) &
        (df['longitude'] >= bbox['lon_min']) &
        (df['longitude'] <= bbox['lon_max'])
    ]

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Interactive Run Explorer"),

    # Dropdown for city selection
    dcc.Dropdown(
        id="city-dropdown",
        options=[{"label": city, "value": city} for city in bounding_boxes["Austria"].keys()],
        value="Leoben"
    ),

    # Radio buttons for HRV method
    dcc.RadioItems(
        id="hrv-method",
        options=[
            {"label": "Standard Deviation", "value": "std"},
            {"label": "RMSSD", "value": "rmssd"}
        ],
        value="std",
        labelStyle={"display": "inline-block", "margin-right": "15px"}
    ),

    # Slider for window size
    dcc.Slider(
        id="window-slider",
        min=5, max=60, step=5, value=10,
        marks={i: str(i) for i in range(5, 65, 5)}
    ),

    # Map output
    dcc.Graph(id="map-graph"),

    # HRV time series output
    dcc.Graph(id="hrv-graph")
])

# Callback: update graphs when controls change
@app.callback(
    [Output("map-graph", "figure"),
     Output("hrv-graph", "figure")],
    [Input("city-dropdown", "value"),
     Input("hrv-method", "value"),
     Input("window-slider", "value")]
)
def update_graphs(selected_city, method, window):
    bbox = bounding_boxes["Austria"][selected_city]
    df_filtered = filter_by_bbox(df_selected.copy(), bbox)
    df_hrv = add_hrv_metrics(df_filtered, window=window, method=method)

    # Map visualization
    map_fig = px.scatter_mapbox(
        df_hrv, lat="latitude", lon="longitude", color="hrv",
        title=f"Runs in {selected_city} ({method.upper()} HRV)",
        mapbox_style="open-street-map"
    )

    # HRV time series
    hrv_fig = px.line(
        df_hrv, x=df_hrv.index, y="hrv",
        title=f"HRV ({method.upper()}) over Time"
    )

    return map_fig, hrv_fig

if __name__ == "__main__":
    app.run(debug=True)