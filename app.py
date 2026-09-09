import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import numpy as np

# Page Layout
st.set_page_config(page_title="Ocean In-Situ Explorer (MoES/INCOIS)", layout="wide")

# Custom Dark Theme Styling matching reference UI
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    div[data-testid="stSidebar"] { background-color: #161b22; }
    .metric-card {
        background-color: #161b22;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #30363d;
        margin-bottom: 8px;
    }
    .status-badge {
        color: #3fb950;
        font-weight: bold;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header Banner
st.title("🌊 Ocean In-Situ Explorer (MoES/INCOIS)")
st.caption("Ministry of Earth Sciences (MoES) / INCOIS • 3D Ocean Model & Observation Platform")

@st.cache_data
def load_data():
    return pd.read_csv("data/live_argo_sample.csv")

df = load_data()

# ---------------------------------------------------------
# SIDEBAR: VISUALIZATION CONTROLS
# ---------------------------------------------------------
st.sidebar.header("VISUALIZATION CONTROLS (v1.5)")

ocean_var = st.sidebar.selectbox(
    "OCEAN VARIABLE", 
    ["Potential Temperature (°C)", "Salinity (PSU)"]
)

subsurface_mode = st.sidebar.toggle("SUBSURFACE MODE (X-Ray Penetration)", value=True)

depth_layer = st.sidebar.selectbox(
    "DEPTH SLICE LAYER", 
    ["All Depths (Volume View)", "Surface (10m)", "Intermediate (100m)", "Deep (1000m)"]
)

opacity = st.sidebar.slider("LAYER OPACITY", 0.1, 1.0, 0.45, step=0.05)
vert_exag = st.sidebar.slider("VERTICAL EXAGGERATION", 1.0, 5.0, 1.8, step=0.1)

# ---------------------------------------------------------
# MAIN DASHBOARD LAYOUT
# ---------------------------------------------------------
col_left, col_center, col_right = st.columns([1.2, 2.5, 1.3])

with col_left:
    st.markdown("""
        <div class="metric-card">
            <b>Domain: Arabian Sea (Domain 1)</b><br>
            <small>LAT: 8.0°N - 18.0°N</small><br>
            <small>LON: 65.0°E - 83.0°E</small><br>
            <small>BATHYMETRY: 0 - 2000 m</small>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Numerical Model Metrics")
    m1, m2 = st.columns(2)
    m1.metric("Temp RMSE", "0.35 °C")
    m2.metric("Mean Bias", "+0.18 °C")
    st.metric("Pearson Correlation (R)", "0.991")

with col_center:
    st.subheader("3D Volume & Iso-Surface Rendering")
    
    # Generate 3D Layer Slices for PyDeck
    slice_data = []
    depths = [10, 100, 500, 1000] if depth_layer == "All Depths (Volume View)" else [10]
    
    for d in depths:
        sub_df = df[df["depth_m"] == d].copy()
        sub_df["elevation"] = (1000 - d) * vert_exag
        slice_data.append(sub_df)
    
    render_df = pd.concat(slice_data) if slice_data else df

    layer = pdk.Layer(
        "ColumnLayer",
        data=render_df,
        get_position=["longitude", "latitude"],
        get_elevation="elevation",
        elevation_scale=5,
        radius=22000,
        get_fill_color="[255 - (temperature_c * 7), 120, temperature_c * 8, int(" + str(int(opacity * 255)) + ")]",
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=12.0,
        longitude=76.5,
        zoom=4.8,
        pitch=55,
        bearing=20
    )

    st.pydeck_chart(pdk.Deck(
        map_provider="carto",
        map_style="dark",
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Float: {float_id}\nDepth: {depth_m}m\nTemp: {temperature_c}°C\nSalinity: {salinity_psu} PSU"}
    ))

with col_right:
    st.markdown('<span class="status-badge">● LIVE SYNC</span>', unsafe_allow_html=True)
    st.subheader("In-Situ Observations")
    
    selected_float = st.selectbox("Selected Platform", df["float_id"].unique())
    float_df = df[df["float_id"] == selected_float].sort_values("depth_m")

    # Profile Chart
    fig = px.line(
        float_df, 
        x="temperature_c", 
        y="depth_m", 
        title=f"Depth vs Temp Profile ({selected_float})",
        labels={"temperature_c": "Temp (°C)", "depth_m": "Depth (m)"}
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=10, r=10, t=30, b=10),
        height=220
    )
    st.plotly_chart(fig, use_container_width=True)

    # Metadata Panel
    latest = float_df.iloc[0]
    st.markdown(f"""
        <div class="metric-card">
            <small><b>SELECTED METADATA</b></small><br>
            <b>Buoy Position:</b> {latest['latitude']}°N, {latest['longitude']}°E<br>
            <b>Payload:</b> Bio-Argo (CTS-4)<br>
            <b>Cycle:</b> #112 | <b>Status:</b> Active
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# BOTTOM COMPARISON PANEL: INCOIS-ROMS VS ARGO
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📊 Numerical Model VS In-Situ Observation Comparison (INCOIS-ROMS vs ARGO TELEMETRY)")

comp_df = pd.DataFrame({
    "Depth Layer": ["Surface (10m)", "50m", "100m", "200m", "500m", "1000m"],
    "INCOIS-ROMS Forecast": ["28.9 °C", "26.2 °C", "22.1 °C", "18.4 °C", "11.5 °C", "6.1 °C"],
    "Argo In-Situ Observed": ["28.5 °C", "26.5 °C", "21.8 °C", "18.1 °C", "11.3 °C", "6.2 °C"],
    "Bias (A - I)": ["-0.40 °C", "+0.30 °C", "-0.30 °C", "-0.30 °C", "-0.20 °C", "+0.10 °C"],
    "Assimilation Confidence": ["98.5%", "96.2%", "95.1%", "94.8%", "92.0%", "90.5%"]
})

st.dataframe(comp_df, use_container_width=True, hide_index=True)