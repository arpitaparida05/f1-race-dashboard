import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="F1 Race Telemetry & Strategy Dashboard", layout="wide")
st.title("🏎️ F1 Race Strategy & Degradation Dashboard")

# Sidebar race selectors
st.sidebar.header("Session Selection")
year = st.sidebar.selectbox("Year", [2024], index=0)
grand_prix = st.sidebar.selectbox("Grand Prix", ["Monaco", "Bahrain", "Silverstone", "Monza"], index=0)

@st.cache_data
def load_race_laps(year_val, gp_val):
    file_path = f"data/{year_val}_{gp_val.lower()}_laps.csv"
    if not os.path.exists(file_path):
        st.error(f"Data file {file_path} not found.")
        st.stop()
        
    clean_laps = pd.read_csv(file_path)
    driver_codes = sorted([str(d) for d in clean_laps["Driver"].dropna().unique()])
    return clean_laps, driver_codes

laps, driver_codes = load_race_laps(year, grand_prix)

# Sidebar driver comparisons
st.sidebar.header("Driver Comparison")
default_d1 = "VER" if "VER" in driver_codes else driver_codes[0]
default_d2 = "LEC" if "LEC" in driver_codes else driver_codes[1]

driver1 = st.sidebar.selectbox("Primary Driver", driver_codes, index=driver_codes.index(default_d1))
driver2 = st.sidebar.selectbox("Comparison Driver", driver_codes, index=driver_codes.index(default_d2))

d1_laps = laps[laps["Driver"] == driver1]
d2_laps = laps[laps["Driver"] == driver2]

# --- Visual 1: Lap-by-Lap Pace Comparison ---
st.subheader(f"1. Lap Pace: {driver1} vs {driver2}")

fig_pace = go.Figure()
fig_pace.add_trace(go.Scatter(x=d1_laps["LapNumber"], y=d1_laps["LapTimeSeconds"], mode="lines+markers", name=driver1))
fig_pace.add_trace(go.Scatter(x=d2_laps["LapNumber"], y=d2_laps["LapTimeSeconds"], mode="lines+markers", name=driver2))
fig_pace.update_layout(
    xaxis_title="Lap Number",
    yaxis_title="Lap Time (seconds)",
    template="plotly_dark",
    hovermode="x unified"
)
st.plotly_chart(fig_pace, use_container_width=True)

# --- Visual 2: Tyre Degradation Across Stints ---
st.subheader(f"2. Tyre Degradation: {driver1} vs {driver2}")
col1, col2 = st.columns(2)

with col1:
    fig_d1_tyres = px.scatter(
        d1_laps,
        x="TyreLife",
        y="LapTimeSeconds",
        color="Compound",
        title=f"{driver1} - Pace vs. Tyre Age",
        trendline="ols"
    )
    fig_d1_tyres.update_layout(template="plotly_dark")
    st.plotly_chart(fig_d1_tyres, use_container_width=True)

with col2:
    fig_d2_tyres = px.scatter(
        d2_laps,
        x="TyreLife",
        y="LapTimeSeconds",
        color="Compound",
        title=f"{driver2} - Pace vs. Tyre Age",
        trendline="ols"
    )
    fig_d2_tyres.update_layout(template="plotly_dark")
    st.plotly_chart(fig_d2_tyres, use_container_width=True)

# --- Visual 3: Session Track Evolution ---
st.subheader("3. Track Evolution (Overall Grid)")
fig_evolution = px.box(
    laps,
    x="LapNumber",
    y="LapTimeSeconds",
    title="Grid Lap Time Distribution Across Race Distance",
    points=False
)
fig_evolution.update_layout(
    template="plotly_dark",
    yaxis_range=[laps["LapTimeSeconds"].quantile(0.02), laps["LapTimeSeconds"].quantile(0.95)]
)
st.plotly_chart(fig_evolution, use_container_width=True)