import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.set_page_config(page_title="INCOIS 3D Ocean Prototype", layout="wide")

st.title("🌊 INCOIS 3D Ocean In-Situ Observation Platform")
st.caption("Problem Statement 26067 | Interactive 3D Spatial Rendering Prototype")

@st.cache_data
def load_data():
    return pd.read_csv("data/live_argo_sample.csv")

df = load_data()

# Sidebar Controls
st.sidebar.header("3D Rendering Controls")
max_depth = st.sidebar.slider("Filter Max Depth (meters)", 0, 1200, 1000, step=50)

filtered_df = df[df["depth_m"] <= max_depth].copy()

# Visual Panel Layout
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("3D Spatial Ocean Column View (EEZ Region)")
    
    # Map elevation inversely to depth for visual 3D extrusion
    filtered_df["elevation"] = filtered_df["depth_m"] * 2
    
    view_state = pdk.ViewState(
        latitude=12.0,
        longitude=78.0,
        zoom=4.5,
        pitch=50,
        bearing=15
    )

    layer = pdk.Layer(
        "ColumnLayer",
        data=filtered_df,
        get_position=["longitude", "latitude"],
        get_elevation="elevation",
        elevation_scale=10,
        radius=15000,
        get_fill_color="[255 - (temperature_c * 5), 100, temperature_c * 8, 200]",
        pickable=True,
        auto_highlight=True,
    )

    # Configured explicitly with CARTO tiles for guaranteed cloud rendering
    st.pydeck_chart(pdk.Deck(
        map_provider="carto",
        map_style="dark",
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Float: {float_id}\nDepth: {depth_m}m\nTemp: {temperature_c}°C\nSalinity: {salinity_psu} PSU"}
    ))

with col2:
    st.subheader("Vertical Profile Telemetry")
    selected_float = st.selectbox("Select Float Instrument", df["float_id"].unique())
    float_data = df[df["float_id"] == selected_float].sort_values("depth_m")
    
    st.metric("Surface Temp (°C)", f"{float_data['temperature_c'].iloc[0]} °C")
    st.metric("Deep Temp at 1000m (°C)", f"{float_data['temperature_c'].iloc[-1]} °C")

    fig = px.line(
        float_data, 
        x="temperature_c", 
        y="depth_m", 
        title=f"Depth vs Temperature ({selected_float})",
        labels={"temperature_c": "Temperature (°C)", "depth_m": "Depth (m)"}
    )
    fig.update_yaxes(autorange="reversed")  # Depth increases downwards
    st.plotly_chart(fig, use_container_width=True)