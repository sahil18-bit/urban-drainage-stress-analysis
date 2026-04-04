import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import inject_css, check_columns, get_degradation_col, run_drain_analysis, show_stat_cards, DRAIN_REQUIRED_COLS, MAP_WEBSITE_URL

st.set_page_config(page_title="Drain Analysis · City Infrastructure", page_icon="🌧️", layout="wide")
inject_css()

with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 1.5rem 0;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:1rem;">
        <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0;">🏙️ City Infrastructure</div>
        <div style="font-size:0.72rem;color:#475569;margin-top:0.2rem;">Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Navigation**")
    st.page_link("main.py",             label="🏠  Home")
    st.page_link("pages/1_drain.py",    label="🌧️  Drain Analysis")
    st.page_link("pages/2_pipe.py",     label="🔧  Pipe Analysis")
    st.page_link("pages/3_map.py",      label="🗺️  Map Viewer")
    st.page_link("pages/4_insights.py", label="📊  Insights")
    
    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"""<a href="{MAP_WEBSITE_URL}" target="_blank" style="display:block;background:linear-gradient(135deg,#1d4ed8,#1e40af);color:#fff;text-decoration:none;padding:0.5rem 0.8rem;border-radius:8px;font-size:0.8rem;font-weight:600;text-align:center;">🗺️ Open Map Viewer ↗</a>""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────
st.markdown("""
<div class="page-title">
    <h1>🌧️ Drain Analysis</h1>
    <p>Physics engine computes utilization per monthly row · Random Forest predicts failure probability · Month column preserved in output</p>
</div>
""", unsafe_allow_html=True)

# ── Required columns info ─────────────────────────────────────────────
with st.expander("ℹ️ Required columns & how the pipeline works", expanded=False):
    st.markdown("""
    <div style="color:#94a3b8;font-size:0.85rem;line-height:1.8;">
    <strong style="color:#7dd3fc;">Physics Engine formulas (per row):</strong><br>
    <code>Q_runoff = Rainfall_mm_hr × Catchment_km2 × Runoff_coeff × 100</code><br>
    <code>Q_baseflow = 5 × Catchment_km2 × Impervious_frac</code><br>
    <code>Q_total_in = Q_runoff + Q_baseflow</code><br>
    <code>Q_eff = Design_Capacity_m3hr × Degradation_Factor</code><br>
    <code>Utilization = Q_total_in / Q_eff</code><br><br>
    <strong style="color:#7dd3fc;">Status thresholds:</strong>
    &nbsp; &lt;0.6 = SAFE &nbsp; 0.6–0.9 = STRESSED &nbsp; &gt;0.9 = CRITICAL<br><br>
    <strong style="color:#7dd3fc;">Required columns:</strong>
    Drain_ID · Rainfall_mm_hr · Catchment_km2 · Impervious_frac · Runoff_coeff · Design_Capacity_m3hr · Degradation_Factor (or Degradation_Factor_x)
    </div>
    """, unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.6], gap="large")

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📁 Upload Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Upload your monthly drain condition CSV file</div>', unsafe_allow_html=True)

    drain_file = st.file_uploader("", type=['csv'], key='drain_upload', label_visibility="collapsed")

    if drain_file:
        try:
            drain_df = pd.read_csv(drain_file)
            unique_drains = drain_df['Drain_ID'].nunique() if 'Drain_ID' in drain_df.columns else '?'
            months = drain_df['Month'].nunique() if 'Month' in drain_df.columns else '?'

            st.markdown(f"""
            <div class="success-box">
                <p>✅ <strong>{len(drain_df):,}</strong> rows loaded &nbsp;·&nbsp; <strong>{unique_drains}</strong> unique drains &nbsp;·&nbsp; <strong>{months}</strong> months</p>
            </div>
            """, unsafe_allow_html=True)

            missing  = check_columns(drain_df, DRAIN_REQUIRED_COLS)
            deg_col  = get_degradation_col(drain_df)
            if deg_col is None:
                missing.append('Degradation_Factor (or Degradation_Factor_x)')

            if missing:
                st.markdown(f"""
                <div class="error-box">
                    <h4>❌ Missing Required Columns</h4>
                    <ul>{''.join(f'<li><code>{c}</code></li>' for c in missing)}</ul>
                    <p style="color:#fca5a5;margin-top:0.5rem;font-size:0.82rem;">Add these columns and re-upload.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-box"><p>✅ All columns found · using <code>{deg_col}</code> for degradation</p></div>', unsafe_allow_html=True)

                with st.expander("👁️ Preview data"):
                    st.dataframe(drain_df.head(8), use_container_width=True)

                run_btn = st.button("▶ Run Drain Analysis", key='run_drain')

        except Exception as e:
            st.error(f"Could not read file: {e}")
    else:
        st.markdown("""
        <div style="border:2px dashed rgba(255,255,255,0.08);border-radius:10px;padding:2rem;text-align:center;color:#334155;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">📂</div>
            <div style="font-size:0.85rem;">Drop your CSV here or click to browse</div>
        </div>
        """, unsafe_allow_html=True)
        run_btn = False

    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    if drain_file and not missing and run_btn:
        with st.spinner("⚙️ Running physics engine + Random Forest ML..."):
            try:
                result = run_drain_analysis(drain_df)
                st.session_state['drain_result'] = result
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                result = None
    else:
        result = st.session_state.get('drain_result', None)

    if result is not None:
        # Stats
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Results Overview</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        show_stat_cards(result, 'Operational_Status', 'Failure_Probability')
        st.markdown('</div>', unsafe_allow_html=True)

        # Charts row
        ch1, ch2 = st.columns(2)
        with ch1:
            status_counts = result['Operational_Status'].value_counts()
            fig_pie = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.55,
                marker_colors=['#4ade80','#fb923c','#f87171'],
                textinfo='label+percent',
                textfont_size=11,
            )])
            fig_pie.update_layout(
                title=dict(text="Status Distribution", font=dict(color='#94a3b8', size=13)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'), showlegend=False,
                margin=dict(t=40,b=10,l=10,r=10), height=220
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with ch2:
            top_drains = result.groupby('Drain_ID')['Failure_Probability'].max().nlargest(8).reset_index()
            top_drains['label'] = top_drains['Drain_ID'].astype(str).apply(lambda x: f"D-{x}")
            fig_bar = go.Figure(go.Bar(
                x=top_drains['label'],
                y=(top_drains['Failure_Probability']*100).round(1),
                marker_color='#ef4444',
                marker_line_width=0,
            ))
            fig_bar.update_layout(
                title=dict(text="Top 8 Riskiest Drains (%)", font=dict(color='#94a3b8',size=13)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#64748b'), xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                margin=dict(t=40,b=10,l=10,r=10), height=220
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Highlight card
        top_per_drain = result.groupby('Drain_ID')['Failure_Probability'].max().reset_index()
        top1_id  = top_per_drain.nlargest(1,'Failure_Probability').iloc[0]['Drain_ID']
        top1_row = result[result['Drain_ID']==top1_id].nlargest(1,'Failure_Probability').iloc[0]
        label    = top1_row.get('Drain_Label', f"Drain #{int(top1_row['Drain_ID'])}")
        month    = int(top1_row['Month']) if 'Month' in top1_row else 'N/A'

        st.markdown(f"""
        <div class="risk-card">
            <div class="risk-card-title">⚠️ Most Likely to Fail First</div>
            <div class="risk-card-id">{label}</div>
            <div class="risk-card-meta">
                Failure Probability: <strong>{top1_row['Failure_Probability']*100:.1f}%</strong> &nbsp;·&nbsp;
                Status: <strong>{top1_row['Operational_Status']}</strong> &nbsp;·&nbsp;
                Utilization: <strong>{top1_row['Utilization_Ratio']*100:.1f}%</strong> &nbsp;·&nbsp;
                Peak Month: <strong>{month}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Top 5 table
        st.markdown('<div class="section-header" style="margin-top:1rem;">🔴 Top 5 Highest Risk Rows</div>', unsafe_allow_html=True)
        show_cols = [c for c in ['Drain_ID','Drain_Label','Month','Operational_Status','Utilization_Ratio','Failure_Probability'] if c in result.columns]
        top5 = result.nlargest(5,'Failure_Probability')[show_cols].copy()
        top5['Failure_Probability'] = (top5['Failure_Probability']*100).round(1).astype(str)+'%'
        top5['Utilization_Ratio']   = (top5['Utilization_Ratio']*100).round(1).astype(str)+'%'
        st.dataframe(top5, use_container_width=True, hide_index=True)

        # Download
        csv_out = result.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Results CSV", csv_out, "drain_evaluation_results.csv", "text/csv", key='drain_dl')

    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:3rem;min-height:300px;display:flex;flex-direction:column;align-items:center;justify-content:center;">
            <div style="font-size:3rem;margin-bottom:1rem;opacity:0.3;">📊</div>
            <div style="color:#334155;font-size:0.9rem;">Upload a CSV and run analysis to see results here</div>
        </div>
        """, unsafe_allow_html=True)
