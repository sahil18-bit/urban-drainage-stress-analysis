import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import inject_css, MAP_WEBSITE_URL

st.set_page_config(page_title="Insights · City Infrastructure", page_icon="📊", layout="wide")
inject_css()

with st.sidebar:
    st.markdown("""<div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:1rem;">
        <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;">🏙️ City Infrastructure</div>
        <div style="font-size:0.72rem;color:#475569;margin-top:0.2rem;">Intelligence Platform</div></div>""", unsafe_allow_html=True)
    st.markdown("**Navigation**")
    st.markdown("""
<div style="display:flex;flex-direction:column;gap:0.3rem;">
    <a href="/" style="color:#94a3b8;text-decoration:none;padding:0.5rem 0.8rem;border-radius:7px;font-size:0.88rem;">🏠&nbsp; Home</a>
    <a href="/1_drain" style="color:#94a3b8;text-decoration:none;padding:0.5rem 0.8rem;border-radius:7px;font-size:0.88rem;">🌧️&nbsp; Drain Analysis</a>
    <a href="/2_pipe" style="color:#94a3b8;text-decoration:none;padding:0.5rem 0.8rem;border-radius:7px;font-size:0.88rem;">🔧&nbsp; Pipe Analysis</a>
    <a href="/3_map" style="color:#94a3b8;text-decoration:none;padding:0.5rem 0.8rem;border-radius:7px;font-size:0.88rem;">🗺️&nbsp; Map Viewer</a>
    <a href="/4_insights" style="color:#94a3b8;text-decoration:none;padding:0.5rem 0.8rem;border-radius:7px;font-size:0.88rem;">📊&nbsp; Insights</a>
    <a href="/5_about" style="color:#94a3b8;text-decoration:none;padding:0.5rem 0.8rem;border-radius:7px;font-size:0.88rem;">ℹ️&nbsp; About</a>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-title">
    <h1>📊 Insights Dashboard</h1>
    <p>Risk distribution, trend analysis, and key performance indicators from your last analysis run</p>
</div>
""", unsafe_allow_html=True)

drain_result = st.session_state.get('drain_result', None)
pipe_result  = st.session_state.get('pipe_result', None)

if drain_result is None and pipe_result is None:
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
        <div style="color:#e2e8f0;font-size:1rem;font-weight:600;margin-bottom:0.5rem;">No Analysis Data Yet</div>
        <div style="color:#475569;font-size:0.88rem;margin-bottom:1.5rem;">Run drain or pipe analysis first, then come back here to see insights.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── KPI Row ───────────────────────────────────────────────────────────
st.markdown("""<div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:1rem;">Key Performance Indicators</div>""", unsafe_allow_html=True)

kpi_cols = st.columns(6)
kpis = []

if drain_result is not None:
    dr = drain_result
    kpis += [
        (str(dr['Drain_ID'].nunique()), "Drains Analyzed", "#4ade80"),
        (f"{(dr['Operational_Status']=='CRITICAL').mean()*100:.1f}%", "Drain Critical %", "#f87171"),
        (f"{dr['Failure_Probability'].mean()*100:.1f}%", "Avg Drain Risk", "#fb923c"),
    ]

if pipe_result is not None:
    pr = pipe_result
    kpis += [
        (str(len(pr)), "Pipes Analyzed", "#60a5fa"),
        (f"{(pr['Pipe_Status']=='CRITICAL').mean()*100:.1f}%", "Pipe Critical %", "#f87171"),
        (f"{pr['Failure_Probability'].mean()*100:.1f}%", "Avg Pipe Risk", "#fb923c"),
    ]

for col, (val, label, color) in zip(kpi_cols, kpis[:6]):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="color:{color};font-size:1.6rem;">{val}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Drain charts ──────────────────────────────────────────────────────
if drain_result is not None:
    st.markdown("""<div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:1rem;">🌧️ Drain Insights</div>""", unsafe_allow_html=True)

    dc1, dc2 = st.columns(2)

    with dc1:
        # Monthly trend — average utilization per month
        if 'Month' in drain_result.columns:
            monthly = drain_result.groupby('Month').agg(
                Avg_Util=('Utilization_Ratio','mean'),
                Critical_Count=('Operational_Status', lambda x: (x=='CRITICAL').sum()),
                Avg_Risk=('Failure_Probability','mean')
            ).reset_index()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly['Month'], y=(monthly['Avg_Util']*100).round(1),
                mode='lines+markers', name='Avg Utilization %',
                line=dict(color='#60a5fa',width=2),
                marker=dict(size=6),
                fill='tozeroy', fillcolor='rgba(96,165,250,0.08)'
            ))
            fig.add_trace(go.Scatter(
                x=monthly['Month'], y=(monthly['Avg_Risk']*100).round(1),
                mode='lines+markers', name='Avg Risk %',
                line=dict(color='#f87171',width=2,dash='dot'),
                marker=dict(size=5)
            ))
            fig.update_layout(
                title=dict(text="Monthly Utilization & Risk Trend", font=dict(color='#94a3b8',size=13)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#64748b'),
                xaxis=dict(showgrid=False, title='Month'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='%'),
                legend=dict(font=dict(size=10,color='#64748b'), bgcolor='rgba(0,0,0,0)'),
                margin=dict(t=40,b=30,l=40,r=10), height=260
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Month column not found — monthly trend unavailable")

    with dc2:
        # Risk distribution histogram
        fig_hist = go.Figure(go.Histogram(
            x=drain_result['Failure_Probability']*100,
            nbinsx=20,
            marker_color='#818cf8',
            marker_line_width=0,
        ))
        fig_hist.update_layout(
            title=dict(text="Failure Probability Distribution", font=dict(color='#94a3b8',size=13)),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            xaxis=dict(showgrid=False, title='Failure Probability (%)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='Count'),
            margin=dict(t=40,b=30,l=40,r=10), height=260
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Most at risk zone
    top_per_drain = drain_result.groupby('Drain_ID')['Failure_Probability'].max().reset_index()
    top1_id  = top_per_drain.nlargest(1,'Failure_Probability').iloc[0]['Drain_ID']
    top1_row = drain_result[drain_result['Drain_ID']==top1_id].nlargest(1,'Failure_Probability').iloc[0]
    label    = top1_row.get('Drain_Label', f"Drain #{int(top1_row['Drain_ID'])}")

    st.markdown(f"""
    <div class="risk-card">
        <div class="risk-card-title">🎯 Most At-Risk Zone — Drain</div>
        <div class="risk-card-id">{label}</div>
        <div class="risk-card-meta">
            Failure Probability: <strong>{top1_row['Failure_Probability']*100:.1f}%</strong> &nbsp;·&nbsp;
            Status: <strong>{top1_row['Operational_Status']}</strong> &nbsp;·&nbsp;
            Utilization: <strong>{top1_row['Utilization_Ratio']*100:.1f}%</strong>
            {'&nbsp;·&nbsp; Peak at Month: <strong>' + str(int(top1_row["Month"])) + '</strong>' if 'Month' in top1_row else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Pipe charts ───────────────────────────────────────────────────────
if pipe_result is not None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:600;margin-bottom:1rem;">🔧 Pipe Insights</div>""", unsafe_allow_html=True)

    pc1, pc2 = st.columns(2)

    with pc1:
        # Material risk comparison
        mat_risk = pipe_result.groupby('Material').agg(
            Avg_Risk=('Failure_Probability','mean'),
            Count=('Pipe_ID','count')
        ).reset_index().sort_values('Avg_Risk', ascending=True)

        fig_mat = go.Figure(go.Bar(
            y=mat_risk['Material'],
            x=(mat_risk['Avg_Risk']*100).round(1),
            orientation='h',
            marker_color='#8b5cf6',
            text=(mat_risk['Avg_Risk']*100).round(1).astype(str)+'%',
            textposition='outside',
        ))
        fig_mat.update_layout(
            title=dict(text="Avg Risk by Material", font=dict(color='#94a3b8',size=13)),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=False),
            margin=dict(t=40,b=10,l=10,r=60), height=280
        )
        st.plotly_chart(fig_mat, use_container_width=True)

    with pc2:
        # Age vs failure probability scatter
        fig_scatter = go.Figure(go.Scatter(
            x=pipe_result['Pipe_Age'],
            y=pipe_result['Failure_Probability']*100,
            mode='markers',
            marker=dict(
                color=pipe_result['Failure_Probability']*100,
                colorscale=[[0,'#4ade80'],[0.5,'#fb923c'],[1,'#f87171']],
                size=6, opacity=0.7,
            ),
            text=pipe_result['Pipe_ID'],
        ))
        fig_scatter.update_layout(
            title=dict(text="Pipe Age vs Failure Probability", font=dict(color='#94a3b8',size=13)),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#64748b'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='Pipe Age (years)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='Failure Probability (%)'),
            margin=dict(t=40,b=30,l=40,r=10), height=280
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    top_pipe = pipe_result.nlargest(1,'Failure_Probability').iloc[0]
    st.markdown(f"""
    <div class="risk-card">
        <div class="risk-card-title">🎯 Most At-Risk Zone — Pipe</div>
        <div class="risk-card-id">{top_pipe['Pipe_ID']} — {top_pipe['Material']}</div>
        <div class="risk-card-meta">
            Failure Probability: <strong>{top_pipe['Failure_Probability']*100:.1f}%</strong> &nbsp;·&nbsp;
            Status: <strong>{top_pipe['Pipe_Status']}</strong> &nbsp;·&nbsp;
            Age: <strong>{int(top_pipe['Pipe_Age'])} years</strong> &nbsp;·&nbsp;
            Degradation: <strong>{top_pipe['Degradation_Factor']:.2f}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
