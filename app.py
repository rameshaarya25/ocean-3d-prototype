import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Page Configuration & Glassmorphism Styling
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

# 2. Sidebar Controls
with st.sidebar:
    st.title("🌐 Ocean Explorer")
    st.caption("3D Ocean Model & Observation Platform")
    
    st.markdown("**VARIABLE**")
    variable = st.selectbox("Select Variable", ["Temperature (°C)", "Salinity (PSU)"])
    
    st.markdown("**DEPTH CUTOFF**")
    max_depth = st.slider("Max Depth View (m)", 500, 6000, 4000, step=500)
    
    st.markdown("**OVERLAYS**")
    show_buoys = st.checkbox("In-situ Instruments", value=True)
    show_model = st.checkbox("Model Slice Data", value=True)
    
    st.markdown("**SETTINGS**")
    color_scale = st.selectbox("Color Scale", ["Rainbow", "Jet", "Viridis", "Thermal", "Turbo"])

# 3. Dynamic Variable Mapping Function
@st.cache_data
def generate_3d_ocean_block(selected_var, depth_limit):
    x = np.linspace(60, 90, 25)   # Longitude (60E to 90E)
    y = np.linspace(5, 25, 25)    # Latitude (5N to 25N)
    z = np.linspace(0, depth_limit, 20)  # Depth
    
    X, Y, Z = np.meshgrid(x, y, z)
    
    if "Temperature" in selected_var:
        # Realistic Temperature: Warm surface (~28°C) decaying with depth (~2°C)
        values = 28.0 * np.exp(-Z / 800.0) + np.sin(X/5) * np.cos(Y/5) * 1.5
        v_min, v_max = 2.0, 29.0
        unit = "°C"
        title = "Temp (°C)"
    else:
        # Realistic Salinity: Lower surface salinity (~34 PSU), halocline peak at depth (~35.5 PSU)
        values = 34.0 + 1.5 * (1 - np.exp(-Z / 600.0)) + np.cos(X/4) * np.sin(Y/4) * 0.2
        v_min, v_max = 33.5, 36.0
        unit = "PSU"
        title = "Salinity (PSU)"
        
    return X, Y, Z, values, v_min, v_max, unit, title

X, Y, Z, values, v_min, v_max, unit, title_label = generate_3d_ocean_block(variable, max_depth)

# 4. Main Header
col_title, col_time, col_view = st.columns([3, 2, 1])
with col_title:
    st.markdown("### 🌊 Ocean In-Situ Explorer")
    st.caption("Real-Time INCOIS-ROMS Model vs Argo In-Situ Telemetry")
with col_time:
    st.date_input("Simulation Epoch", value=pd.to_datetime("2026-09-08"))
with col_view:
    st.button("3D Volume View", disabled=True)

# 5. Build 3D Volumetric Plotly Rendering
fig_3d = go.Figure()

# Add Volumetric Ocean Block (Dynamic Variable Data)
fig_3d.add_trace(go.Isosurface(
    x=X.flatten(),
    y=Y.flatten(),
    z=Z.flatten(),
    value=values.flatten(),
    isomin=v_min,
    isomax=v_max,
    surface_count=6,
    colorscale=color_scale.lower(),
    colorbar=dict(title=title_label, x=-0.05, len=0.7),
    caps=dict(x_show=True, y_show=True, z_show=False),
    slices_z=dict(show=show_model, locations=[10, int(max_depth/2), int(max_depth*0.8)]),
    opacity=0.85
))

# Add Floating 3D Instrument Buoys & Tether Cables
if show_buoys:
    buoy_lons = [68.0, 75.0, 82.0, 72.0, 85.0]
    buoy_lats = [12.0, 18.0, 10.0, 22.0, 15.0]
    
    fig_3d.add_trace(go.Scatter3d(
        x=buoy_lons, y=buoy_lats, z=[0]*len(buoy_lons),
        mode='markers+text',
        marker=dict(size=8, color='#f59e0b', symbol='diamond', line=dict(color='#ffffff', width=1)),
        text=["Argo_6902746", "Argo_5906001", "Moored_BD02", "Glider_IN01", "Argo_5906002"],
        textposition="top center",
        name="In-Situ Instruments"
    ))
    
    for blon, blat in zip(buoy_lons, buoy_lats):
        fig_3d.add_trace(go.Scatter3d(
            x=[blon, blon], y=[blat, blat], z=[0, max_depth*0.85],
            mode='lines',
            line=dict(color='#38bdf8', width=2, dash='dot'),
            showlegend=False
        ))

# Camera Layout
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

# 6. Render Layout Panels
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
    
    st.markdown(f"#### Depth Profile ({variable.split()[0]})")
    
    p_depths = np.linspace(0, max_depth, 10)
    if "Temperature" in variable:
        p_vals = 28.0 * np.exp(-p_depths / 800.0)
    else:
        p_vals = 34.0 + 1.5 * (1 - np.exp(-p_depths / 600.0))
    
    fig_prof = go.Figure(go.Scatter(x=p_vals, y=p_depths, mode='lines+markers', line=dict(color='#38bdf8', width=2)))
    fig_prof.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=title_label,
        yaxis=dict(title="Depth (m)", autorange="reversed")
    )
    st.plotly_chart(fig_prof, use_container_width=True)

# 7. Dynamic Comparison Section
st.markdown("---")
st.markdown(f"#### MODEL VS IN-SITU COMPARISON ({variable})")

b1, b2, b3 = st.columns(3)

if "Temperature" in variable:
    m1, i1, m2, i2, m3, i3 = "29.1°C", "28.7°C", "12.4°C", "11.8°C", "6.2°C", "5.7°C"
    d1, d2, d3 = "-0.4°C", "-0.6°C", "-0.5°C"
else:
    m1, i1, m2, i2, m3, i3 = "34.1 PSU", "34.3 PSU", "35.2 PSU", "35.1 PSU", "35.5 PSU", "35.4 PSU"
    d1, d2, d3 = "+0.2 PSU", "-0.1 PSU", "-0.1 PSU"

with b1:
    st.markdown(f"""
        <div class="css-card">
            <b>Surface (0m)</b><br>
            Model: {m1} &nbsp;|&nbsp; In-situ: {i1}<br>
            <span style="color:#ef4444;">Difference: {d1}</span>
        </div>
    """, unsafe_allow_html=True)
with b2:
    st.markdown(f"""
        <div class="css-card">
            <b>Mid Depth (1000m)</b><br>
            Model: {m2} &nbsp;|&nbsp; In-situ: {i2}<br>
            <span style="color:#ef4444;">Difference: {d2}</span>
        </div>
    """, unsafe_allow_html=True)
with b3:
    st.markdown(f"""
        <div class="css-card">
            <b>Deep Ocean (2000m)</b><br>
            Model: {m3} &nbsp;|&nbsp; In-situ: {i3}<br>
            <span style="color:#ef4444;">Difference: {d3}</span>
        </div>
    """, unsafe_allow_html=True)