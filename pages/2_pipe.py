import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import inject_css, check_columns, run_pipe_analysis, show_stat_cards, PIPE_REQUIRED_COLS, MAP_WEBSITE_URL

st.set_page_config(page_title="Pipe Analysis · City Infrastructure", page_icon="🔧", layout="wide")
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

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"""<a href="{MAP_WEBSITE_URL}" target="_blank" style="display:block;background:linear-gradient(135deg,#1d4ed8,#1e40af);color:#fff;text-decoration:none;padding:0.5rem 0.8rem;border-radius:8px;font-size:0.8rem;font-weight:600;text-align:center;">🗺️ Open Map Viewer ↗</a>""", unsafe_allow_html=True)

st.markdown("""
<div class="page-title">
    <h1>🔧 Pipe Analysis</h1>
    <p>Manning's equation computes hydraulic capacity · Age-based degradation model · Random Forest predicts failure probability</p>
</div>
""", unsafe_allow_html=True)

with st.expander("ℹ️ How pipe analysis works", expanded=False):
    st.markdown("""
    <div style="color:#94a3b8;font-size:0.85rem;line-height:1.8;">
    <strong style="color:#7dd3fc;">Manning's Equation (capacity):</strong><br>
    <code>Capacity = (1/n) × A × R^(2/3) × S^(1/2)</code><br>
    where n = roughness coefficient, A = cross-sectional area, R = hydraulic radius, S = slope<br><br>
    <strong style="color:#7dd3fc;">Degradation by material:</strong><br>
    Vitrified Clay / Brick / Cast Iron → fastest decay &nbsp;·&nbsp; Concrete → moderate &nbsp;·&nbsp; PVC / HDPE → slowest<br><br>
    <strong style="color:#7dd3fc;">Required columns:</strong>
    Pipe_ID · Diameter_in · Slope_pct · Material · Install_Date
    </div>
    """, unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.6], gap="large")

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📁 Upload Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Upload your pipe infrastructure CSV file</div>', unsafe_allow_html=True)

    pipe_file = st.file_uploader("", type=['csv'], key='pipe_upload', label_visibility="collapsed")

    if pipe_file:
        try:
            pipe_df = pd.read_csv(pipe_file)
            st.markdown(f"""
            <div class="success-box"><p>✅ <strong>{len(pipe_df):,}</strong> pipes loaded &nbsp;·&nbsp; <strong>{len(pipe_df.columns)}</strong> columns</p></div>
            """, unsafe_allow_html=True)

            missing = check_columns(pipe_df, PIPE_REQUIRED_COLS)
            if missing:
                st.markdown(f"""
                <div class="error-box">
                    <h4>❌ Missing Required Columns</h4>
                    <ul>{''.join(f'<li><code>{c}</code></li>' for c in missing)}</ul>
                    <p style="color:#fca5a5;margin-top:0.5rem;font-size:0.82rem;">Add these columns and re-upload.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box"><p>✅ All required columns found. Ready to run.</p></div>', unsafe_allow_html=True)

                # Material breakdown
                if 'Material' in pipe_df.columns:
                    mat_counts = pipe_df['Material'].value_counts()
                    st.markdown("<br>**Material breakdown:**", unsafe_allow_html=False)
                    for mat, cnt in mat_counts.head(5).items():
                        pct = cnt/len(pipe_df)*100
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;font-size:0.8rem;">
                            <div style="color:#94a3b8;width:160px;truncate;">{mat[:22]}</div>
                            <div style="flex:1;background:rgba(255,255,255,0.05);border-radius:4px;height:6px;">
                                <div style="width:{pct:.0f}%;background:#1d4ed8;height:6px;border-radius:4px;"></div>
                            </div>
                            <div style="color:#475569;width:30px;text-align:right;">{cnt}</div>
                        </div>
                        """, unsafe_allow_html=True)

                with st.expander("👁️ Preview data"):
                    st.dataframe(pipe_df.head(8), use_container_width=True)

                run_btn = st.button("▶ Run Pipe Analysis", key='run_pipe')

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
        missing = []

    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    if pipe_file and not missing and run_btn:
        with st.spinner("⚙️ Running Manning's equation + Random Forest ML..."):
            try:
                result = run_pipe_analysis(pipe_df)
                st.session_state['pipe_result'] = result
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                result = None
    else:
        result = st.session_state.get('pipe_result', None)

    if result is not None:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Results Overview</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        show_stat_cards(result, 'Pipe_Status', 'Failure_Probability')
        st.markdown('</div>', unsafe_allow_html=True)

        ch1, ch2 = st.columns(2)
        with ch1:
            status_counts = result['Pipe_Status'].value_counts()
            colors = {'SAFE':'#4ade80','STRESSED':'#fb923c','CRITICAL':'#f87171'}
            fig_pie = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.55,
                marker_colors=[colors.get(l,'#64748b') for l in status_counts.index],
                textinfo='label+percent', textfont_size=11,
            )])
            fig_pie.update_layout(
                title=dict(text="Pipe Status Distribution", font=dict(color='#94a3b8',size=13)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'), showlegend=False,
                margin=dict(t=40,b=10,l=10,r=10), height=220
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with ch2:
            # Age distribution of critical pipes
            critical = result[result['Pipe_Status']=='CRITICAL']
            if len(critical) > 0:
                fig_age = go.Figure(go.Histogram(
                    x=critical['Pipe_Age'], nbinsx=12,
                    marker_color='#ef4444', marker_line_width=0,
                ))
                fig_age.update_layout(
                    title=dict(text="Age of Critical Pipes (yrs)", font=dict(color='#94a3b8',size=13)),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#64748b'),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                    margin=dict(t=40,b=10,l=10,r=10), height=220
                )
                st.plotly_chart(fig_age, use_container_width=True)

        # Aging insight card
        if 'Pipe_Age' in result.columns:
            avg_age  = result['Pipe_Age'].mean()
            old_pct  = (result['Pipe_Age'] > 80).mean() * 100
            st.markdown(f"""
            <div class="glass-card" style="border-left:3px solid #8b5cf6;">
                <div style="color:#c4b5fd;font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">🏗️ Infrastructure Aging Insights</div>
                <div style="display:flex;gap:2rem;">
                    <div><div style="color:#ffffff;font-size:1.4rem;font-weight:700;">{avg_age:.0f} yrs</div><div style="color:#64748b;font-size:0.75rem;">Average pipe age</div></div>
                    <div><div style="color:#f87171;font-size:1.4rem;font-weight:700;">{old_pct:.1f}%</div><div style="color:#64748b;font-size:0.75rem;">Pipes older than 80 years</div></div>
                    <div><div style="color:#fb923c;font-size:1.4rem;font-weight:700;">{result['Degradation_Factor'].mean():.2f}</div><div style="color:#64748b;font-size:0.75rem;">Avg degradation factor</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Highlight card
        top1 = result.nlargest(1,'Failure_Probability').iloc[0]
        st.markdown(f"""
        <div class="risk-card">
            <div class="risk-card-title">⚠️ Most Likely to Fail First</div>
            <div class="risk-card-id">{top1['Pipe_ID']} — {top1['Material']}</div>
            <div class="risk-card-meta">
                Failure Probability: <strong>{top1['Failure_Probability']*100:.1f}%</strong> &nbsp;·&nbsp;
                Status: <strong>{top1['Pipe_Status']}</strong> &nbsp;·&nbsp;
                Age: <strong>{int(top1['Pipe_Age'])} yrs</strong> &nbsp;·&nbsp;
                Utilization: <strong>{top1['Utilization']*100:.1f}%</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header" style="margin-top:1rem;">🔴 Top 5 Highest Risk Pipes</div>', unsafe_allow_html=True)
        top5 = result.nlargest(5,'Failure_Probability')[['Pipe_ID','Material','Pipe_Age','Pipe_Status','Utilization','Failure_Probability']].copy()
        top5['Failure_Probability'] = (top5['Failure_Probability']*100).round(1).astype(str)+'%'
        top5['Utilization']         = (top5['Utilization']*100).round(1).astype(str)+'%'
        st.dataframe(top5, use_container_width=True, hide_index=True)

        csv_out = result.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Results CSV", csv_out, "pipe_evaluation_results.csv", "text/csv", key='pipe_dl')

    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:3rem;">
            <div style="font-size:3rem;margin-bottom:1rem;opacity:0.3;">🔧</div>
            <div style="color:#334155;font-size:0.9rem;">Upload a CSV and run analysis to see results here</div>
        </div>
        """, unsafe_allow_html=True)
