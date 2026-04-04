import streamlit as st
from utils import inject_css, MAP_WEBSITE_URL

st.set_page_config(
    page_title="Urban Infrastructure Intelligence Platform",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_css()

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem 0; border-bottom:1px solid rgba(255,255,255,0.06); margin-bottom:1rem;">
        <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;">🏙️ City Infrastructure</div>
        <div style="font-size:0.72rem;color:#475569;margin-top:0.2rem;">Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Navigation**")
    st.page_link("main.py",               label="🏠  Home",             )
    st.page_link("pages/1_drain.py",      label="🌧️  Drain Analysis"    )
    st.page_link("pages/2_pipe.py",       label="🔧  Pipe Analysis"     )
    st.page_link("pages/3_map.py",        label="🗺️  Map Viewer"        )
    st.page_link("pages/4_insights.py",   label="📊  Insights"          )
    st.page_link("pages/5_about.py",      label="ℹ️  About"             )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:0.75rem;color:#334155;">
        <div style="margin-bottom:0.5rem;color:#475569;">Map Viewer</div>
        <a href="{MAP_WEBSITE_URL}" target="_blank" style="
            display:block;background:linear-gradient(135deg,#1d4ed8,#1e40af);
            color:#fff;text-decoration:none;padding:0.5rem 0.8rem;border-radius:8px;
            font-size:0.8rem;font-weight:600;text-align:center;
            border:1px solid rgba(41,121,255,0.4);">
            🗺️ Open Map Viewer ↗
        </a>
    </div>
    """, unsafe_allow_html=True)

# ── Hero Section ──────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b3e 50%, #0a1628 100%);
    border: 1px solid rgba(41,121,255,0.15);
    border-radius: 24px;
    padding: 4rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
">
    <div style="
        position:absolute;top:-80px;right:-80px;
        width:400px;height:400px;
        background:radial-gradient(circle,rgba(29,78,216,0.15) 0%,transparent 70%);
        border-radius:50%;
    "></div>
    <div style="
        position:absolute;bottom:-60px;left:-60px;
        width:300px;height:300px;
        background:radial-gradient(circle,rgba(41,121,255,0.08) 0%,transparent 70%);
        border-radius:50%;
    "></div>
    <div style="position:relative;z-index:1;">
        <div style="
            display:inline-block;
            background:rgba(41,121,255,0.1);
            border:1px solid rgba(41,121,255,0.25);
            border-radius:20px;padding:0.3rem 1rem;
            font-size:0.75rem;color:#93c5fd;font-weight:600;
            letter-spacing:0.1em;text-transform:uppercase;
            margin-bottom:1.2rem;
        ">AI-Powered Infrastructure Monitoring</div>
        <h1 style="
            color:#ffffff;font-size:2.8rem;font-weight:800;
            margin:0 0 1rem 0;line-height:1.15;
            background:linear-gradient(135deg,#ffffff,#93c5fd);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        ">Urban Infrastructure<br>Intelligence Platform</h1>
        <p style="color:#64748b;font-size:1.05rem;margin:0 0 2.5rem 0;max-width:560px;line-height:1.6;">
            AI-powered drainage and pipe risk monitoring system for smart city planning and flood prevention.
            Upload raw data, run physics-based ML analysis, and get actionable risk insights.
        </p>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;">
            <a href="/drain" target="_self" style="
                background:linear-gradient(135deg,#1d4ed8,#1e40af);
                color:#ffffff;text-decoration:none;
                padding:0.75rem 2rem;border-radius:10px;
                font-weight:600;font-size:0.95rem;
                border:1px solid rgba(41,121,255,0.4);
                box-shadow:0 4px 20px rgba(29,78,216,0.35);
            ">▶ Start Analysis</a>
            <a href="{MAP_WEBSITE_URL}" target="_blank" style="
                background:rgba(255,255,255,0.05);
                color:#93c5fd;text-decoration:none;
                padding:0.75rem 2rem;border-radius:10px;
                font-weight:600;font-size:0.95rem;
                border:1px solid rgba(255,255,255,0.1);
            ">🗺️ View Map</a>
        </div>
    </div>
</div>
""".replace("{MAP_WEBSITE_URL}", MAP_WEBSITE_URL), unsafe_allow_html=True)

# ── Feature Cards ─────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
    <div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:1rem;">
        Platform Capabilities
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

cards = [
    ("🌧️", "Drain Monitoring", "Physics-based flow analysis using Manning's equation across 12-month rainfall cycles", "#0ea5e9"),
    ("🔧", "Pipe Risk Prediction", "Random Forest ML model predicts failure probability using age, material and hydraulic capacity", "#8b5cf6"),
    ("⚠️", "Failure Alerts", "Color-coded severity system identifies CRITICAL assets requiring immediate maintenance", "#ef4444"),
    ("🗺️", "Map Visualization", "Geospatial mapping of drain and pipe status with month-wise filtering for field teams", "#10b981"),
]

for col, (icon, title, desc, color) in zip([c1,c2,c3,c4], cards):
    with col:
        st.markdown(f"""
        <div class="glass-card" style="border-top:3px solid {color}22;min-height:180px;">
            <div style="font-size:1.8rem;margin-bottom:0.8rem;">{icon}</div>
            <div style="color:#e2e8f0;font-weight:600;font-size:0.95rem;margin-bottom:0.5rem;">{title}</div>
            <div style="color:#475569;font-size:0.8rem;line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── System stats ──────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:1rem;">
    System Overview
</div>
""", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
stats = [
    ("300", "Drain Points Monitored", "#4ade80"),
    ("300", "Pipe Segments Tracked", "#60a5fa"),
    ("12", "Months of Rainfall Data", "#a78bfa"),
    ("2", "ML Models Deployed", "#fb923c"),
]
for col, (val, label, color) in zip([s1,s2,s3,s4], stats):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:{color};">{val}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Pipeline flow ─────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="glass-card">
    <div style="color:#e2e8f0;font-weight:600;font-size:0.95rem;margin-bottom:1.2rem;">⚙️ Analysis Pipeline</div>
    <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;">
        <div style="background:rgba(29,78,216,0.15);border:1px solid rgba(29,78,216,0.3);border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:#93c5fd;">📁 Raw CSV Upload</div>
        <div style="color:#334155;font-size:1.2rem;">→</div>
        <div style="background:rgba(139,92,246,0.15);border:1px solid rgba(139,92,246,0.3);border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:#c4b5fd;">⚡ Physics Engine</div>
        <div style="color:#334155;font-size:1.2rem;">→</div>
        <div style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:#6ee7b7;">🤖 Random Forest ML</div>
        <div style="color:#334155;font-size:1.2rem;">→</div>
        <div style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:#fca5a5;">📊 Failure Probability</div>
        <div style="color:#334155;font-size:1.2rem;">→</div>
        <div style="background:rgba(251,146,60,0.15);border:1px solid rgba(251,146,60,0.3);border-radius:8px;padding:0.5rem 1rem;font-size:0.82rem;color:#fed7aa;">⬇️ CSV Output</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#1e293b;font-size:0.75rem;padding:2rem 0 1rem 0;margin-top:2rem;border-top:1px solid rgba(255,255,255,0.04);">
    Urban Infrastructure Intelligence Platform &nbsp;•&nbsp; Physics Engine + Random Forest ML &nbsp;•&nbsp; Seattle SPU Dataset
</div>
""", unsafe_allow_html=True)
