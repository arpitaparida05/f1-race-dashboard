import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="F1 Pit-Wall Telemetry Console",
    page_icon="🏎️",
    layout="wide"
)

# --- Custom F1 Theme CSS ---
st.markdown("""
<style>
    /* Global style tweaks */
    .stApp {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #8b949e;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f0f6fc;
        margin-top: 4px;
    }
    .badge-f1 {
        background-color: #e10600;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.75rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# --- Pirelli Compound Color Map ---
COMPOUND_COLORS = {
    "SOFT": "#FF3333",
    "MEDIUM": "#FFD700",
    "HARD": "#FFFFFF",
    "INTERMEDIATE": "#39B54A",
    "WET": "#00AEEF"
}

# --- Dynamic Dataset Scanner ---
def get_available_sessions():
    data_dir = "data"
    if not os.path.exists(data_dir):
        return {}
    
    files = [f for f in os.listdir(data_dir) if f.endswith("_laps.csv")]
    session_map = {}
    for f in files:
        parts = f.replace("_laps.csv", "").split("_")
        if len(parts) >= 2:
            yr = int(parts[0])
            gp = parts[1].capitalize()
            session_map.setdefault(yr, []).append(gp)
            
    return session_map

available_sessions = get_available_sessions()

if not available_sessions:
    st.error("No lap files found in data/ directory. Run fetch_data.py first.")
    st.stop()

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("### 🏎️ **Session Control**")
    available_years = sorted(list(available_sessions.keys()), reverse=True)
    year = st.selectbox("Season", available_years, index=0)
    
    available_gps = sorted(available_sessions[year])
    grand_prix = st.selectbox("Grand Prix", available_gps, index=0)
    st.divider()

# --- Data Loading ---
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

# Driver Selectors
with st.sidebar:
    st.markdown("### ⚔️ **Head-to-Head Drivers**")
    default_d1 = "VER" if "VER" in driver_codes else driver_codes[0]
    default_d2 = "LEC" if "LEC" in driver_codes else (driver_codes[1] if len(driver_codes) > 1 else driver_codes[0])

    driver1 = st.selectbox("Primary Driver", driver_codes, index=driver_codes.index(default_d1))
    driver2 = st.selectbox("Comparison Driver", driver_codes, index=driver_codes.index(default_d2))
    st.caption("Pit laps & in/out laps are excluded from degradation regressions.")

# Filter lap records
d1_laps = laps[laps["Driver"] == driver1].sort_values("LapNumber")
d2_laps = laps[laps["Driver"] == driver2].sort_values("LapNumber")

# --- Title Header ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title(f"{year} {grand_prix} Grand Prix")
    st.caption("Telemetry analysis & stint degradation engine | Pit-wall stream")
with col_head2:
    st.markdown("<div style='text-align: right; padding-top: 15px;'><span class='badge-f1'>LIVE TIMING ARCHIVE</span></div>", unsafe_allow_html=True)

# --- KPI Metric Banner ---
def format_laptime(seconds):
    if pd.isna(seconds):
        return "N/A"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"

d1_best = d1_laps["LapTimeSeconds"].min()
d2_best = d2_laps["LapTimeSeconds"].min()
delta_best = d1_best - d2_best

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{driver1} Best Lap</div>
        <div class="metric-value">{format_laptime(d1_best)}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{driver2} Best Lap</div>
        <div class="metric-value">{format_laptime(d2_best)}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    delta_display = f"{delta_best:+.3f}s"
    delta_color = "#39B54A" if delta_best < 0 else "#FF3333"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Head-to-Head Delta</div>
        <div class="metric-value" style="color: {delta_color};">{delta_display}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    total_laps_analyzed = len(d1_laps)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Laps Analyzed ({driver1})</div>
        <div class="metric-value">{total_laps_analyzed}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Main Analytical Tabs ---
tab_pace, tab_degradation, tab_evolution, tab_data = st.tabs([
    "📈 Lap Pace Comparison", 
    "🧪 Tyre Degradation (OLS)", 
    "🔄 Circuit Track Evolution", 
    "📋 Telemetry Data Table"
])

with tab_pace:
    st.markdown(f"#### Race Pace Distribution: **{driver1}** vs **{driver2}**")
    fig_pace = go.Figure()
    fig_pace.add_trace(go.Scatter(
        x=d1_laps["LapNumber"],
        y=d1_laps["LapTimeSeconds"],
        mode="lines+markers",
        name=driver1,
        line=dict(color="#FF1801", width=2.5),
        marker=dict(size=6)
    ))
    fig_pace.add_trace(go.Scatter(
        x=d2_laps["LapNumber"],
        y=d2_laps["LapTimeSeconds"],
        mode="lines+markers",
        name=driver2,
        line=dict(color="#00D2BE", width=2.5),
        marker=dict(size=6)
    ))
    fig_pace.update_layout(
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (Seconds)",
        template="plotly_dark",
        hovermode="x unified",
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_pace, use_container_width=True)

with tab_degradation:
    st.markdown("#### Stint Degradation Regression by Compound")
    c1, c2 = st.columns(2)
    
    with c1:
        fig_d1_tyres = px.scatter(
            d1_laps,
            x="TyreLife",
            y="LapTimeSeconds",
            color="Compound",
            color_discrete_map=COMPOUND_COLORS,
            title=f"{driver1} — Tyre Age vs Lap Time",
            trendline="ols"
        )
        fig_d1_tyres.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22"
        )
        st.plotly_chart(fig_d1_tyres, use_container_width=True)

    with c2:
        fig_d2_tyres = px.scatter(
            d2_laps,
            x="TyreLife",
            y="LapTimeSeconds",
            color="Compound",
            color_discrete_map=COMPOUND_COLORS,
            title=f"{driver2} — Tyre Age vs Lap Time",
            trendline="ols"
        )
        fig_d2_tyres.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22"
        )
        st.plotly_chart(fig_d2_tyres, use_container_width=True)

with tab_evolution:
    st.markdown("#### Grip Accumulation & Circuit Lap Time Evolution")
    fig_evolution = px.box(
        laps,
        x="LapNumber",
        y="LapTimeSeconds",
        title="Field-wide Lap Time Range per Lap",
        points=False,
        color_discrete_sequence=["#e10600"]
    )
    fig_evolution.update_layout(
        template="plotly_dark",
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        yaxis_range=[laps["LapTimeSeconds"].quantile(0.02), laps["LapTimeSeconds"].quantile(0.95)]
    )
    st.plotly_chart(fig_evolution, use_container_width=True)

with tab_data:
    st.markdown("#### Cleaned Lap Telemetry Slices")
    st.dataframe(
        laps[laps["Driver"].isin([driver1, driver2])][["Driver", "LapNumber", "LapTimeSeconds", "Compound", "TyreLife", "Stint"]],
        use_container_width=True,
        hide_index=True
    )