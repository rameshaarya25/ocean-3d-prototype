import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Page Configuration & Professional Glassmorphism CSS
st.set_page_config(page_title="Ocean In-Situ Explorer", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #050811; color: #e1e7ed; }
    div[data-testid="stSidebar"] { background-color: #0b0f19; border-right: 1px solid #1e293b; }
    .css-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .status-pill {
        background-color: #064e3b;
        color: #34d399;
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar Controls (Matching Reference Layout)
with st.sidebar:
    st.title("🌐 Ocean Explorer")
    st.caption("3D Ocean Model & Observation Platform")
    
    st.markdown("**VARIABLE**")
    variable = st.selectbox("Select Variable", ["Temperature (°C)", "Salinity (PSU)"])
    
    st.markdown("**DEPTH CUTOFF**")
    max_depth = st.slider("Max Depth View (m)", 0, 6000, 4000, step=500)
    
    st.markdown("**OVERLAYS**")
    show_buoys = st.checkbox("In-situ Instruments", value=True)
    show_model = st.checkbox("Model Slice Data", value=True)
    
    st.markdown("**SETTINGS**")
    color_scale = st.selectbox("Color Scale", ["Rainbow", "Jet", "Viridis", "Thermal", "Turbo"])

# 3. Main Header & Top Controls
col_title, col_time, col_view = st.columns([3, 2, 1])
with col_title:
    st.markdown("### 🌊 Ocean In-Situ Explorer")
    st.caption("Real-Time INCOIS-ROMS Model vs Argo In-Situ Telemetry")
with col_time:
    st.date_input("Simulation Epoch", value=pd.to_datetime("2026-09-08"))
with col_view:
    st.button("3D Volume View", disabled=True)

# 4. Generate Volumetric 3D Dataset
@st.cache_data
def generate_3d_ocean_block():
    x = np.linspace(60, 90, 25)   # Longitude (60E to 90E)
    y = np.linspace(5, 25, 25)    # Latitude (5N to 25N)
    z = np.linspace(0, 4000, 20)  # Depth (0m to 4000m)
    
    X, Y, Z = np.meshgrid(x, y, z)
    # Simulate realistic vertical ocean profile (warm surface, cold deep water)
    values = 28.0 * np.exp(-Z / 800.0) + np.sin(X/5) * np.cos(Y/5) * 1.5
    return X, Y, Z, values

X, Y, Z, values = generate_3d_ocean_block()

# 5. Build 3D Volumetric Plotly Rendering
fig_3d = go.Figure()

# Add Volumetric Ocean Block (Isosurface Slices)
fig_3d.add_trace(go.Isosurface(
    x=X.flatten(),
    y=Y.flatten(),
    z=Z.flatten(),
    value=values.flatten(),
    isomin=2,
    isomax=29,
    surface_count=6,
    colorscale=color_scale.lower(),
    colorbar=dict(title="Temp (°C)", x=-0.05, len=0.7),
    caps=dict(x_show=True, y_show=True, z_show=False),
    slices_z=dict(show=True, locations=[10, 1000, 2000]),
    opacity=0.85
))

# Add Floating 3D Instrument Buoys & Tether Cables
if show_buoys:
    buoy_lons = [68.0, 75.0, 82.0, 72.0, 85.0]
    buoy_lats = [12.0, 18.0, 10.0, 22.0, 15.0]
    
    # Yellow Floating Markers at Surface
    fig_3d.add_trace(go.Scatter3d(
        x=buoy_lons, y=buoy_lats, z=[0]*len(buoy_lons),
        mode='markers+text',
        marker=dict(size=8, color='#f59e0b', symbol='diamond', line=dict(color='#ffffff', width=1)),
        text=["Argo_6902746", "Argo_5906001", "Moored_BD02", "Glider_IN01", "Argo_5906002"],
        textposition="top center",
        name="In-Situ Instruments"
    ))
    
    # Vertical Tether Cables going into the deep ocean
    for blon, blat in zip(buoy_lons, buoy_lats):
        fig_3d.add_trace(go.Scatter3d(
            x=[blon, blon], y=[blat, blat], z=[0, 3500],
            mode='lines',
            line=dict(color='#38bdf8', width=2, dash='dot'),
            showlegend=False
        ))

# Camera Layout & Dark Horizon Theme Configuration
fig_3d.update_layout(
    template="plotly_dark",
    paper_bgcolor="#050811",
    plot_bgcolor="#050811",
    margin=dict(l=0, r=0, t=0, b=0),
    height=550,
    scene=dict(
        xaxis=dict(title="Longitude (°E)", backgroundcolor="#0b0f19", gridcolor="#1e293b"),
        yaxis=dict(title="Latitude (°N)", backgroundcolor="#0b0f19", gridcolor="#1e293b"),
        zaxis=dict(title="Depth (m)", autorange="reversed", backgroundcolor="#0b0f19", gridcolor="#1e293b"),
        camera=dict(
            eye=dict(x=-1.6, y=-1.6, z=1.2),
            center=dict(x=0, y=0, z=-0.2)
        ),
        aspectratio=dict(x=1.2, y=1, z=0.8)
    )
)

# Render 3D Dashboard Block & Right Telemetry Column
c_main, c_right = st.columns([3, 1])

with c_main:
    st.plotly_chart(fig_3d, use_container_width=True)

with c_right:
    st.markdown('<span class="status-pill">● IN-SITU INSTRUMENTS LIVE</span>', unsafe_allow_html=True)
    st.markdown("#### Instrument Info")
    
    st.markdown("""
        <div class="css-card">
            <small><b>ID:</b> 6902746</small><br>
            <small><b>Type:</b> Bio-Argo Float (CTS-4)</small><br>
            <small><b>Position:</b> 12.45°N, 65.23°E</small><br>
            <small><b>Depth Range:</b> 0 - 2000 m</small>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Depth Profile")
    # Quick Profile Line Chart
    p_depths = np.array([0, 100, 500, 1000, 2000, 3000, 4000])
    p_temps = 28.0 * np.exp(-p_depths / 800.0)
    
    fig_prof = go.Figure(go.Scatter(x=p_temps, y=p_depths, mode='lines+markers', line=dict(color='#38bdf8', width=2)))
    fig_prof.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Temp (°C)",
        yaxis=dict(title="Depth (m)", autorange="reversed")
    )
    st.plotly_chart(fig_prof, use_container_width=True)

# 6. Bottom Model Comparison Bar
st.markdown("---")
st.markdown("#### MODEL VS IN-SITU COMPARISON (At Selected Location)")

b1, b2, b3 = st.columns(3)
with b1:
    st.markdown("""
        <div class="css-card">
            <b>Surface Temp (0m)</b><br>
            Model: 29.1°C &nbsp;|&nbsp; In-situ: 28.7°C<br>
            <span style="color:#ef4444;">Difference: -0.4°C</span>
        </div>
    """, unsafe_allow_html=True)
with b2:
    st.markdown("""
        <div class="css-card">
            <b>Temp at 1000m</b><br>
            Model: 12.4°C &nbsp;|&nbsp; In-situ: 11.8°C<br>
            <span style="color:#ef4444;">Difference: -0.6°C</span>
        </div>
    """, unsafe_allow_html=True)
with b3:
    st.markdown("""
        <div class="css-card">
            <b>Temp at 2000m</b><br>
            Model: 6.2°C &nbsp;|&nbsp; In-situ: 5.7°C<br>
            <span style="color:#ef4444;">Difference: -0.5°C</span>
        </div>
    """, unsafe_allow_html=True)