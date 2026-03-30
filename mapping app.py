import streamlit as st
import geopandas as gpd
import pandas as pd
import pydeck as pdk
from shapely import wkt




#------------DASHBOARD---------------#

def show_dashboard(df):
    st.subheader("📊 Evaluation Dashboard")

    # -------- KPI METRICS --------
    total = len(df)
    safe = len(df[df["Pipe_Status"] == "SAFE"])
    stressed = len(df[df["Pipe_Status"] == "STRESSED"])
    critical = len(df[df["Pipe_Status"] == "CRITICAL"])

    avg_util = round(df["Utilization"].mean(), 2)
    max_risk = round(df["Failure_Probability"].max(), 2)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Total Pipes", total)
    col2.metric("SAFE", safe)
    col3.metric("STRESSED", stressed)
    col4.metric("CRITICAL", critical)
    col5.metric("Avg Utilization", avg_util)
    col6.metric("Max Risk", max_risk)

    st.divider()

    # -------- RISK DISTRIBUTION --------
    st.subheader("Risk Distribution")
    risk_counts = df["Pipe_Status"].value_counts()
    st.bar_chart(risk_counts)

    st.divider()

    # -------- TOP CRITICAL PIPES --------
    st.subheader("⚠️ Top Critical Pipes")

    critical_df = df[df["Pipe_Status"] == "CRITICAL"] \
                    .sort_values("Failure_Probability", ascending=False) \
                    .head(10)

    st.dataframe(critical_df)

    st.divider()

    # -------- FULL TABLE --------
    st.subheader("Full Evaluation Data")
    st.dataframe(df)

#-------webpage----------#

st.set_page_config(page_title="Urban Drainage System", layout="wide")

st.title("🌧 Urban Drainage Monitoring System")


# ------------------ LOAD DATA ------------------
pipes = gpd.read_file("pipes_final_qgis.geojson")
flows = gpd.read_file("flow_arrows_final_qgis.geojson")
drains = pd.read_csv("Data evaluation results3.csv")

# Convert CRS
pipes = pipes.to_crs(epsg=4326)
flows = flows.to_crs(epsg=4326)

@st.cache_data
def load_pipes():
    df = pd.read_csv("pipes_qgis.csv")
    
    # Convert geometry column (WKT → geometry)
    df["geometry"] = df["geometry"].apply(wkt.loads)
    
    pipes = gpd.GeoDataFrame(df, geometry="geometry")
    pipes = pipes.set_crs(epsg=4326)
    
    return pipes

# ------------------ SIDEBAR ------------------
st.sidebar.header("Controls")

#----------UPLOAD CSV FILE------------#
st.subheader("Upload Evaluation CSV")
uploaded_file = st.file_uploader(
    "Upload Pipe Evaluation File",
    type=["csv"]
)

run_analysis = st.button("Run Analysis")


#----------------------------#

view_option = st.sidebar.radio(
    "Select View",
    ["Pipes Network", "Drain Nodes"]
)

month = st.sidebar.selectbox(
    "Select Month",
    list(range(1, 13))
)

risk = st.sidebar.selectbox(
    "Select Risk Level",
    ["All", "SAFE", "STRESSED", "CRITICAL"]
)

# ------------------ TITLE ------------------
st.subheader(f"{view_option} - {month}")

# ------------------ PIPES VIEW ------------------
if view_option == "Pipes Network":
    st.write("Showing Pipes Network")

    # -------- STEP 5 : MERGE AFTER UPLOAD --------
    if uploaded_file is not None and run_analysis:

        uploaded_df = pd.read_csv(uploaded_file)

        # remove old evaluation columns (avoid duplicates)
        pipes = pipes.drop(columns=[
            "Utilization",
            "Failure_Probability",
            "Pipe_Status"
        ], errors="ignore")

        # merge new evaluation
        pipes = pipes.merge(uploaded_df, on="Pipe_ID", how="left")

        # Dashboard
        show_dashboard(pipes)

    else:
        st.info("Upload CSV and click Run Analysis to see dashboard")

    # make sure status uppercase (for coloring)
    pipes["Pipe_Status"] = pipes["Pipe_Status"].str.upper()

    # -------- COLOR FUNCTION --------
    def get_pipe_color(status):
        if status == "CRITICAL":
            return [255, 0, 0]
        elif status == "STRESSED":
            return [255, 165, 0]
        elif status == "SAFE":
            return [0, 255, 0]
        else:
            return [200, 200, 200]

    pipes["color"] = pipes["Pipe_Status"].apply(get_pipe_color)

    # Filter
    filtered_pipes = pipes.copy()
    # month filter
    filtered_pipes = filtered_pipes[
        filtered_pipes["Month"] == month
        ]
    # risk filter
    if risk != "All":
        filtered_pipes = filtered_pipes[
            filtered_pipes["Pipe_Status"] == risk
            ]

    if filtered_pipes.empty:
        st.warning("No pipes available for selected risk level")
    else:
        pipes_json = filtered_pipes.__geo_interface__

        layer = pdk.Layer(
            "GeoJsonLayer",
            data=pipes_json,
            get_line_color="properties.color",
            get_line_width=4,
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=filtered_pipes.geometry.centroid.y.mean(),
            longitude=filtered_pipes.geometry.centroid.x.mean(),
            zoom=13,
        )

        tooltip = {
            "html": "<b>Pipe ID:</b> {Pipe_ID} <br/>"
                    "<b>Status:</b> {Pipe_Status} <br/>"
                    "<b>Failure Probability:</b> {Failure_Probability} <br/>"
                    "<b>Utilization:</b> {Utilization} <br/>"
                    "<b>Material:</b> {Material}",
            "style": {"backgroundColor": "black", "color": "white"}
        }

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        ))

    st.subheader("Pipe Data")
    st.dataframe(filtered_pipes)
# ------------------ DRAINS VIEW ------------------
elif view_option == "Drain Nodes":
    st.write("Showing Drain Nodes")

    # Rename columns
    drains = drains.rename(columns={
        "latitude": "lat",
        "longitude": "lon"
    })

    # Convert status to uppercase (important for matching)
    drains["Drain_Status"] = drains["Drain_Status"].str.upper()

    # -------- COLOR FUNCTION --------
    def get_color(status):
        if status == "CRITICAL":
            return [255, 0, 0]      # Red
        elif status == "STRESSED":
            return [255, 165, 0]    # Orange
        elif status == "SAFE":
            return [0, 255, 0]      # Green
        else:
            return [200, 200, 200]

    # Apply color
    drains["color"] = drains["Drain_Status"].apply(get_color)

    # -------- FILTER BY RISK --------
    filtered_drains = drains.copy()
    # month filter
    filtered_drains = filtered_drains[
        filtered_drains["Month"] == month
        ]
    # risk filter
    if risk != "All":
        filtered_drains = filtered_drains[
            filtered_drains["Drain_Status"] == risk
            ]
    filtered_drains["color"] = filtered_drains["Drain_Status"].apply(get_color)

    # -------- HANDLE EMPTY CASE --------
    if filtered_drains.empty:
        st.warning("No data available for selected risk level")
    else:
        # Map layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_drains,
            get_position='[lon, lat]',
            get_fill_color="color",
            get_radius=7,
            pickable=True
        )

        # View settings
        view_state = pdk.ViewState(
            latitude=filtered_drains["lat"].mean(),
            longitude=filtered_drains["lon"].mean(),
            zoom=13
        )
        tooltip = {
            "html": "<b>Drain ID:</b> {Drain_ID} <br/>"
            "<b>Latitude:</b> {lat} <br/>"
            "<b>Longitude:</b> {lon}",
            "style": {
                "backgroundColor": "black",
                "color": "white"
                }
            }

        # Show map
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        ))

    # Show data
    st.subheader("Drain Data")
    st.dataframe(filtered_drains)

