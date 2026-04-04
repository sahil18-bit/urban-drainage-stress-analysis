import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import inject_css, MAP_WEBSITE_URL

st.set_page_config(page_title="Map Viewer · City Infrastructure", page_icon="🗺️", layout="wide")
inject_css()

with st.sidebar:
    st.markdown("""<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:1rem;">
        <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;">🏙️ City Infrastructure</div>
        <div style="font-size:0.72rem;color:#475569;margin-top:0.2rem;">Intelligence Platform</div></div>""", unsafe_allow_html=True)
    st.markdown("**Navigation**")
    st.page_link("main.py",             label="🏠  Home")
    st.page_link("pages/1_drain.py",    label="🌧️  Drain Analysis")
    st.page_link("pages/2_pipe.py",     label="🔧  Pipe Analysis")
    st.page_link("pages/3_map.py",      label="🗺️  Map Viewer")
    st.page_link("pages/4_insights.py", label="📊  Insights")
    st.page_link("pages/5_about.py",    label="ℹ️  About")

st.markdown("""
<div class="page-title">
    <h1>🗺️ Map Viewer</h1>
    <p>Geospatial visualization of drain and pipe status across Seattle's drainage network</p>
</div>
""", unsafe_allow_html=True)

# ── Map CTA ───────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, rgba(13,33,55,0.9), rgba(10,61,98,0.7));
    border: 1px solid rgba(21,101,192,0.4); border-radius: 20px;
    padding: 3rem; text-align: center; margin-bottom: 2rem;
">
    <div style="font-size:4rem;margin-bottom:1rem;">🗺️</div>
    <h2 style="color:#ffffff;margin:0 0 0.5rem 0;font-size:1.5rem;">Interactive Map Viewer</h2>
    <p style="color:#64748b;margin:0 0 2rem 0;max-width:500px;margin-left:auto;margin-right:auto;line-height:1.6;">
        The full interactive map is hosted on our companion Streamlit app.
        Upload your analysis output CSV there to view drain and pipe status on a live map with month-wise filters.
    </p>
    <a href="{MAP_WEBSITE_URL}" target="_blank" style="
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
        color: #ffffff; text-decoration: none;
        padding: 0.9rem 2.5rem; border-radius: 12px;
        font-weight: 700; font-size: 1rem;
        border: 1px solid rgba(41,121,255,0.5);
        box-shadow: 0 4px 20px rgba(29,78,216,0.4);
        display: inline-block;
    ">🚀 Open Map Viewer ↗</a>
</div>
""", unsafe_allow_html=True)

# ── Workflow steps ─────────────────────────────────────────────────────
st.markdown("""
<div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:1rem;">
    How to use the map viewer
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
steps = [
    ("1️⃣", "Run Analysis", "Use Drain or Pipe Analysis page to process your CSV"),
    ("2️⃣", "Download CSV", "Download the output results CSV from the analysis page"),
    ("3️⃣", "Open Map", "Click 'Open Map Viewer' to go to the companion website"),
    ("4️⃣", "Upload & Filter", "Upload the CSV there and use month/status filters"),
]
for col, (num, title, desc) in zip([c1,c2,c3,c4], steps):
    with col:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div style="font-size:1.8rem;margin-bottom:0.5rem;">{num}</div>
            <div style="color:#e2e8f0;font-weight:600;font-size:0.9rem;margin-bottom:0.4rem;">{title}</div>
            <div style="color:#475569;font-size:0.78rem;line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Legend ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="glass-card">
    <div style="color:#e2e8f0;font-weight:600;margin-bottom:1.2rem;">🎨 Map Legend</div>
    <div style="display:flex;gap:2rem;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:14px;height:14px;border-radius:50%;background:#4ade80;"></div>
            <span style="color:#94a3b8;font-size:0.85rem;">SAFE — Utilization &lt; 60%</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:14px;height:14px;border-radius:50%;background:#fb923c;"></div>
            <span style="color:#94a3b8;font-size:0.85rem;">STRESSED — Utilization 60–90%</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:14px;height:14px;border-radius:50%;background:#f87171;"></div>
            <span style="color:#94a3b8;font-size:0.85rem;">CRITICAL — Utilization &gt; 90%</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:14px;height:14px;border-radius:3px;background:#4ade80;"></div>
            <span style="color:#94a3b8;font-size:0.85rem;">Squares = Drains</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:14px;height:14px;border-radius:50%;background:#60a5fa;"></div>
            <span style="color:#94a3b8;font-size:0.85rem;">Circles = Pipes</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Available GeoJSON files info ───────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="glass-card">
    <div style="color:#e2e8f0;font-weight:600;margin-bottom:1rem;">📁 GeoJSON Files for QGIS</div>
    <div style="color:#64748b;font-size:0.83rem;margin-bottom:1rem;">If you prefer offline mapping in QGIS, the following files are available from the analysis pipeline:</div>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:0.8rem;">
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:0.8rem;">
            <div style="color:#7dd3fc;font-size:0.82rem;font-weight:600;">drain_points.geojson</div>
            <div style="color:#475569;font-size:0.75rem;margin-top:0.2rem;">300 drain points with status & failure probability</div>
        </div>
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:0.8rem;">
            <div style="color:#7dd3fc;font-size:0.82rem;font-weight:600;">pipe_lines.geojson</div>
            <div style="color:#475569;font-size:0.75rem;margin-top:0.2rem;">93 pipe segments from upstream to downstream node</div>
        </div>
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:0.8rem;">
            <div style="color:#7dd3fc;font-size:0.82rem;font-weight:600;">pipe_points.geojson</div>
            <div style="color:#475569;font-size:0.75rem;margin-top:0.2rem;">Pipe midpoints with hydraulic attributes</div>
        </div>
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:0.8rem;">
            <div style="color:#7dd3fc;font-size:0.82rem;font-weight:600;">water_flow.geojson</div>
            <div style="color:#475569;font-size:0.75rem;margin-top:0.2rem;">Flow direction from drain to downstream node</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
