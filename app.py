import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Urban Drainage Network Analyzer",
    page_icon="🌊",
    layout="wide"
)

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .block-container { padding-top: 2rem; }
    .title-bar {
        background: linear-gradient(135deg, #1a1f36, #0d47a1);
        border-radius: 12px; padding: 1.5rem 2rem;
        margin-bottom: 1.5rem; border-left: 5px solid #2979ff;
    }
    .title-bar h1 { color: #ffffff; margin: 0; font-size: 1.8rem; }
    .title-bar p  { color: #90caf9; margin: 0.3rem 0 0 0; font-size: 0.95rem; }
    .map-banner {
        background: linear-gradient(135deg, #0d2137, #0a3d62);
        border: 1px solid #1565c0; border-radius: 12px;
        padding: 1rem 1.8rem; margin-bottom: 1.5rem;
        display: flex; align-items: center; justify-content: space-between; gap: 1rem;
    }
    .map-banner-text h3 { color: #90caf9; margin: 0; font-size: 1rem; }
    .map-banner-text p  { color: #546e7a; margin: 0.2rem 0 0 0; font-size: 0.8rem; }
    .map-banner-btn a {
        background: linear-gradient(135deg, #1565c0, #0d47a1);
        color: #ffffff !important; text-decoration: none;
        padding: 0.5rem 1.3rem; border-radius: 8px;
        font-weight: 600; font-size: 0.88rem; white-space: nowrap; border: 1px solid #2979ff;
    }
    .section-card {
        background: #1e2130; border-radius: 12px;
        padding: 1.5rem; border: 1px solid #2a2f45;
    }
    .section-title { color: #ffffff; font-size: 1.15rem; font-weight: 600; margin-bottom: 0.3rem; }
    .section-sub   { color: #7986cb; font-size: 0.82rem; margin-bottom: 1.2rem; }
    .required-cols {
        background: #1a1f36; border-radius: 8px; padding: 0.8rem 1rem;
        margin-bottom: 1rem; font-size: 0.78rem; color: #7986cb; border: 1px solid #2a2f45;
    }
    .required-cols strong { color: #90caf9; }
    .error-box {
        background: #2d1515; border: 1px solid #ef5350;
        border-radius: 8px; padding: 1rem 1.2rem; margin: 0.8rem 0;
    }
    .error-box h4 { color: #ef5350; margin: 0 0 0.5rem 0; }
    .error-box ul { color: #ffcdd2; margin: 0; padding-left: 1.2rem; }
    .error-box li { margin-bottom: 0.3rem; font-size: 0.85rem; }
    .success-box {
        background: #132d1a; border: 1px solid #66bb6a;
        border-radius: 8px; padding: 1rem 1.2rem; margin: 0.8rem 0;
    }
    .success-box p { color: #a5d6a7; margin: 0; }
    .stat-box {
        background: #252a40; border-radius: 8px;
        padding: 0.8rem 1rem; text-align: center; border: 1px solid #2a2f45;
    }
    .stat-value { font-size: 1.6rem; font-weight: 700; color: #ffffff; }
    .stat-label { font-size: 0.75rem; color: #90a4ae; margin-top: 0.2rem; }
    .highlight-card {
        background: linear-gradient(135deg, #2d1515, #1a0a0a);
        border: 1px solid #ef5350; border-radius: 10px;
        padding: 1rem 1.2rem; margin: 0.8rem 0;
    }
    .highlight-card h4     { color: #ef5350; margin: 0 0 0.5rem 0; font-size: 0.92rem; }
    .highlight-card .hc-id { color: #ffffff; font-size: 1.1rem; font-weight: 700; }
    .highlight-card .hc-detail { color: #90a4ae; font-size: 0.82rem; margin-top: 0.3rem; }
    .divider { border: none; border-top: 1px solid #2a2f45; margin: 1.2rem 0; }
    .stButton > button {
        background: linear-gradient(135deg, #1565c0, #0d47a1);
        color: white; border: none; border-radius: 8px;
        padding: 0.6rem 1.5rem; font-weight: 600; width: 100%;
    }
    .stButton > button:hover { background: linear-gradient(135deg, #1976d2, #1565c0); }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────
MAP_WEBSITE_URL = "https://your-mapping-website.streamlit.app"  # 🔁 Replace after deployment

# ── Header ────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-bar">
    <h1>🌊 Urban Drainage Network Analyzer</h1>
    <p>Upload your raw data, run the analysis pipeline, and download results with failure probability predictions.</p>
</div>
""", unsafe_allow_html=True)

# ── Map Banner ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="map-banner">
    <div class="map-banner-text">
        <h3>🗺️ Want to see your drains on a map?</h3>
        <p>Download your output CSV → upload it on the mapping website to view drain & pipe status with month-wise filters.</p>
    </div>
    <div class="map-banner-btn">
        <a href="{MAP_WEBSITE_URL}" target="_blank">Open Map Viewer ↗</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# REQUIRED COLUMNS
# ════════════════════════════════════════════════════════════════════

# physicsengine.py reads these exact columns
# Note: Degradation_Factor may appear as Degradation_Factor_x in dataset
DRAIN_REQUIRED_COLS = [
    'Drain_ID', 'Rainfall_mm_hr', 'Catchment_km2', 'Impervious_frac',
    'Runoff_coeff', 'Design_Capacity_m3hr',
]
# Degradation_Factor checked separately (accepts _x suffix too)

PIPE_REQUIRED_COLS = [
    'Pipe_ID', 'Diameter_in', 'Slope_pct', 'Material', 'Install_Date'
]

def check_columns(df, required):
    return [c for c in required if c not in df.columns]

def get_degradation_col(df):
    """Returns the correct degradation column name — handles both variants."""
    if 'Degradation_Factor' in df.columns:
        return 'Degradation_Factor'
    elif 'Degradation_Factor_x' in df.columns:
        return 'Degradation_Factor_x'
    return None

# ════════════════════════════════════════════════════════════════════
# DRAIN ANALYSIS
# Exact physicsengine.py logic → exact drain_probability.py logic
# No aggregation — Month column preserved in output
# ════════════════════════════════════════════════════════════════════

def run_drain_analysis(df):
    df = df.copy()

    # Get degradation column (handles Degradation_Factor or Degradation_Factor_x)
    deg_col = get_degradation_col(df)

    # ── physicsengine.py — exact formulas, row by row ─────────────────
    df['Q_runoff']        = df['Rainfall_mm_hr'] * df['Catchment_km2'] * df['Runoff_coeff'] * 100
    df['Q_baseflow']      = 5 * df['Catchment_km2'] * df['Impervious_frac']
    df['Q_total_in']      = df['Q_runoff'] + df['Q_baseflow']
    df['Q_eff']           = df['Design_Capacity_m3hr'] * df[deg_col]
    df['Utilization_Ratio'] = df.apply(
        lambda r: r['Q_total_in'] / r['Q_eff'] if r['Q_eff'] != 0 else 0, axis=1
    )

    # Physics engine owns Operational_Status — single source of truth
    def get_status(u):
        if u < 0.6:    return 'SAFE'
        elif u <= 0.9: return 'STRESSED'
        else:          return 'CRITICAL'

    df['Operational_Status'] = df['Utilization_Ratio'].apply(get_status)

    # ── drain_probability.py — ML on every row ────────────────────────
    # Convert status to numeric label (trust physics engine, no reclassify)
    status_to_label = {'SAFE': 0, 'STRESSED': 1, 'CRITICAL': 2}
    df['Status_Label'] = df['Operational_Status'].map(status_to_label)

    features = [
        'Rainfall_mm_hr', 'Impervious_frac',
        deg_col, 'Catchment_km2', 'Runoff_coeff',
    ]
    # Add Slope if present
    if 'Slope' in df.columns:
        features.insert(1, 'Slope')

    features = [f for f in features if f in df.columns]

    X        = df[features].fillna(0)
    y        = df['Status_Label']
    scaler   = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    model.fit(X_train, y_train)

    probs     = model.predict_proba(X_scaled)
    n_classes = probs.shape[1]
    if n_classes == 3:
        df['Failure_Probability'] = probs[:, 1] + probs[:, 2]
    elif n_classes == 2:
        df['Failure_Probability'] = probs[:, 1]
    else:
        df['Failure_Probability'] = 1 - probs[:, 0]

    return df

# ════════════════════════════════════════════════════════════════════
# PIPE ANALYSIS — exact pipe_probability.py
# ════════════════════════════════════════════════════════════════════

def run_pipe_analysis(df):
    def parse_year(val):
        if pd.isna(val): return np.nan
        try:
            return int(str(val)[:4]) if str(val)[:4].isdigit() else pd.to_datetime(val).year
        except:
            return np.nan

    pipes = df.copy()
    pipes['Install_Year'] = pipes['Install_Date'].apply(parse_year)
    pipes['Pipe_Age']     = 2026 - pipes['Install_Year']
    pipes['Pipe_Age']     = pipes['Pipe_Age'].fillna(pipes['Pipe_Age'].median())
    pipes['Slope_pct']    = pipes['Slope_pct'].fillna(pipes['Slope_pct'].median())

    roughness_map = {
        'Concrete': 0.013, 'Reinforced Concrete Pipe': 0.013,
        'Vitrified Clay': 0.014, 'Cast Iron Pipe': 0.015,
        'Ductile Iron Pipe': 0.012, 'Polyvinyl Chloride': 0.009,
        'High Density Polyethylene': 0.011, 'Brick': 0.016,
        'Asbestos Cement': 0.011, 'Unknown': 0.013,
    }
    pipes['Roughness_n']      = pipes['Material'].map(roughness_map).fillna(0.013)
    pipes['Diameter_m']       = pipes['Diameter_in'] * 0.0254
    pipes['Area_m2']          = np.pi * (pipes['Diameter_m'] / 2) ** 2
    pipes['Hydraulic_Radius'] = pipes['Diameter_m'] / 4
    pipes['Slope_safe']       = pipes['Slope_pct'].clip(lower=0.01) / 100

    pipes['Capacity_m3_s'] = (
        (1 / pipes['Roughness_n']) * pipes['Area_m2'] *
        (pipes['Hydraulic_Radius'] ** (2/3)) * (pipes['Slope_safe'] ** 0.5)
    )

    def degradation(row):
        age, mat = row['Pipe_Age'], row['Material']
        if mat in ['Vitrified Clay', 'Brick', 'Asbestos Cement', 'Cast Iron Pipe']:
            return max(0.3, 1 - age * 0.008)
        elif mat in ['Concrete', 'Reinforced Concrete Pipe']:
            return max(0.4, 1 - age * 0.006)
        else:
            return max(0.6, 1 - age * 0.003)

    pipes['Degradation_Factor'] = pipes.apply(degradation, axis=1)
    pipes['Effective_Capacity'] = pipes['Capacity_m3_s'] * pipes['Degradation_Factor']

    np.random.seed(42)
    pipes['Pipe_Flow_m3_s'] = (
        pipes['Effective_Capacity'] *
        (0.4 + 0.5 * (pipes['Pipe_Age'] / pipes['Pipe_Age'].max())) +
        np.random.normal(0, 0.05, len(pipes))
    )
    pipes['Pipe_Flow_m3_s'] = pipes['Pipe_Flow_m3_s'].clip(lower=0)
    pipes['Utilization']    = pipes['Pipe_Flow_m3_s'] / pipes['Effective_Capacity'].replace(0, np.nan)

    def classify(u):
        if u < 0.6:   return 0
        elif u < 0.9: return 1
        else:         return 2

    pipes['Pipe_Status_Label'] = pipes['Utilization'].apply(classify)
    pipes['Pipe_Status']       = pipes['Pipe_Status_Label'].map({0:'SAFE', 1:'STRESSED', 2:'CRITICAL'})

    features = ['Diameter_in', 'Pipe_Age', 'Slope_pct', 'Utilization', 'Degradation_Factor', 'Roughness_n']
    features = [f for f in features if f in pipes.columns]

    X        = pipes[features].fillna(0)
    y        = pipes['Pipe_Status_Label']
    scaler   = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    model.fit(X_train, y_train)

    probs     = model.predict_proba(X_scaled)
    n_classes = probs.shape[1]
    if n_classes == 3:
        pipes['Failure_Probability'] = probs[:, 1] + probs[:, 2]
    elif n_classes == 2:
        pipes['Failure_Probability'] = probs[:, 1]
    else:
        pipes['Failure_Probability'] = 1 - probs[:, 0]

    pipes['Pipe_Status'] = pipes['Pipe_Status_Label'].map({0:'SAFE', 1:'STRESSED', 2:'CRITICAL'})
    return pipes

# ════════════════════════════════════════════════════════════════════
# UI HELPERS
# ════════════════════════════════════════════════════════════════════

def show_stats(df, status_col, prob_col):
    total    = len(df)
    safe     = (df[status_col] == 'SAFE').sum()
    stressed = (df[status_col] == 'STRESSED').sum()
    critical = (df[status_col] == 'CRITICAL').sum()
    avg_prob = df[prob_col].mean() * 100
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-value">{total}</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-value" style="color:#66bb6a">{safe}</div><div class="stat-label">SAFE</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-value" style="color:#ffa726">{stressed}</div><div class="stat-label">STRESSED</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-box"><div class="stat-value" style="color:#ef5350">{critical}</div><div class="stat-label">CRITICAL</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="stat-box"><div class="stat-value">{avg_prob:.1f}%</div><div class="stat-label">Avg Risk</div></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# LAYOUT
# ════════════════════════════════════════════════════════════════════

col_drain, col_pipe = st.columns(2, gap="large")

# ── LEFT: DRAIN ───────────────────────────────────────────────────────
with col_drain:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">🌧️ Drain Analysis</div>
        <div class="section-sub">Upload monthly drain data — physics engine computes utilization per row, ML predicts failure probability. Month column preserved in output.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="required-cols">
        <strong>Required columns:</strong><br>
        {' &nbsp;•&nbsp; '.join(DRAIN_REQUIRED_COLS)} &nbsp;•&nbsp; <em>Degradation_Factor (or Degradation_Factor_x)</em>
    </div>
    """, unsafe_allow_html=True)

    drain_file = st.file_uploader("Upload Drain CSV", type=['csv'], key='drain_upload')

    if drain_file:
        try:
            drain_df = pd.read_csv(drain_file)
            unique_drains = drain_df['Drain_ID'].nunique() if 'Drain_ID' in drain_df.columns else '?'
            st.success(f"✅ File loaded — {len(drain_df)} rows • {unique_drains} unique drains")

            # Check required cols + degradation col separately
            missing = check_columns(drain_df, DRAIN_REQUIRED_COLS)
            deg_col = get_degradation_col(drain_df)
            if deg_col is None:
                missing.append('Degradation_Factor (or Degradation_Factor_x)')

            if missing:
                st.markdown(f"""
                <div class="error-box">
                    <h4>❌ Missing Required Columns</h4>
                    <ul>{''.join(f'<li><code>{c}</code></li>' for c in missing)}</ul>
                    <p style="color:#ffcdd2;margin-top:0.5rem;font-size:0.85rem;">
                    Cannot run analysis without these columns. Please add them and re-upload.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-box"><p>✅ All required columns found (using <code>{deg_col}</code> for degradation). Ready to run.</p></div>', unsafe_allow_html=True)

                with st.expander("Preview uploaded data"):
                    st.dataframe(drain_df.head(10), use_container_width=True)

                if st.button("▶ Run Drain Analysis", key='run_drain'):
                    with st.spinner("Running physics engine + Random Forest..."):
                        try:
                            result = run_drain_analysis(drain_df)
                            st.markdown('<hr class="divider">', unsafe_allow_html=True)
                            st.markdown("**📊 Results**")
                            show_stats(result, 'Operational_Status', 'Failure_Probability')
                            st.markdown("<br>", unsafe_allow_html=True)

                            # Most likely to fail — highest prob per unique drain
                            top_per_drain = result.groupby('Drain_ID')['Failure_Probability'].max().reset_index()
                            top1_id  = top_per_drain.nlargest(1, 'Failure_Probability').iloc[0]['Drain_ID']
                            top1_row = result[result['Drain_ID'] == top1_id].nlargest(1, 'Failure_Probability').iloc[0]
                            label    = top1_row.get('Drain_Label', f"Drain #{int(top1_row['Drain_ID'])}")

                            st.markdown(f"""
                            <div class="highlight-card">
                                <h4>⚠️ Most Likely to Fail First</h4>
                                <div class="hc-id">{label}</div>
                                <div class="hc-detail">
                                    Failure Probability: <strong style="color:#ef5350">{top1_row['Failure_Probability']*100:.1f}%</strong> &nbsp;|&nbsp;
                                    Status: <strong style="color:#ef5350">{top1_row['Operational_Status']}</strong> &nbsp;|&nbsp;
                                    Utilization: <strong>{top1_row['Utilization_Ratio']*100:.1f}%</strong> &nbsp;|&nbsp;
                                    Month: <strong>{int(top1_row['Month']) if 'Month' in top1_row else 'N/A'}</strong>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown("**🔴 Top 5 Highest Risk Rows**")
                            show_cols = [c for c in ['Drain_ID','Drain_Label','Month','Operational_Status','Utilization_Ratio','Failure_Probability'] if c in result.columns]
                            top5 = result.nlargest(5, 'Failure_Probability')[show_cols].copy()
                            top5['Failure_Probability'] = (top5['Failure_Probability']*100).round(1).astype(str) + '%'
                            top5['Utilization_Ratio']   = (top5['Utilization_Ratio']*100).round(1).astype(str) + '%'
                            st.dataframe(top5, use_container_width=True, hide_index=True)

                            csv_out = result.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="⬇️ Download Drain Results CSV",
                                data=csv_out,
                                file_name="drain_evaluation_results.csv",
                                mime="text/csv",
                                key='drain_download'
                            )
                        except Exception as e:
                            st.error(f"Analysis failed: {str(e)}")
        except Exception as e:
            st.error(f"Could not read file: {str(e)}")

# ── RIGHT: PIPE ───────────────────────────────────────────────────────
with col_pipe:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">🔧 Pipe Analysis</div>
        <div class="section-sub">Upload pipe infrastructure data — Manning's equation computes hydraulic capacity, ML predicts failure probability</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="required-cols">
        <strong>Required columns:</strong><br>
        {' &nbsp;•&nbsp; '.join(PIPE_REQUIRED_COLS)}
    </div>
    """, unsafe_allow_html=True)

    pipe_file = st.file_uploader("Upload Pipe CSV", type=['csv'], key='pipe_upload')

    if pipe_file:
        try:
            pipe_df = pd.read_csv(pipe_file)
            st.success(f"✅ File loaded — {len(pipe_df)} rows • {len(pipe_df.columns)} columns")

            missing = check_columns(pipe_df, PIPE_REQUIRED_COLS)
            if missing:
                st.markdown(f"""
                <div class="error-box">
                    <h4>❌ Missing Required Columns</h4>
                    <ul>{''.join(f'<li><code>{c}</code></li>' for c in missing)}</ul>
                    <p style="color:#ffcdd2;margin-top:0.5rem;font-size:0.85rem;">
                    Cannot run analysis without these columns. Please add them and re-upload.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box"><p>✅ All required columns found. Ready to run.</p></div>', unsafe_allow_html=True)

                with st.expander("Preview uploaded data"):
                    st.dataframe(pipe_df.head(10), use_container_width=True)

                if st.button("▶ Run Pipe Analysis", key='run_pipe'):
                    with st.spinner("Running Manning's equation + Random Forest..."):
                        try:
                            result = run_pipe_analysis(pipe_df)
                            st.markdown('<hr class="divider">', unsafe_allow_html=True)
                            st.markdown("**📊 Results**")
                            show_stats(result, 'Pipe_Status', 'Failure_Probability')
                            st.markdown("<br>", unsafe_allow_html=True)

                            top1 = result.nlargest(1, 'Failure_Probability').iloc[0]
                            st.markdown(f"""
                            <div class="highlight-card">
                                <h4>⚠️ Most Likely to Fail First</h4>
                                <div class="hc-id">{top1['Pipe_ID']} — {top1['Material']}</div>
                                <div class="hc-detail">
                                    Failure Probability: <strong style="color:#ef5350">{top1['Failure_Probability']*100:.1f}%</strong> &nbsp;|&nbsp;
                                    Status: <strong style="color:#ef5350">{top1['Pipe_Status']}</strong> &nbsp;|&nbsp;
                                    Age: <strong>{int(top1['Pipe_Age'])} yrs</strong> &nbsp;|&nbsp;
                                    Utilization: <strong>{top1['Utilization']*100:.1f}%</strong>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown("**🔴 Top 5 Highest Risk Pipes**")
                            top5 = result.nlargest(5, 'Failure_Probability')[
                                ['Pipe_ID','Material','Pipe_Age','Pipe_Status','Utilization','Failure_Probability']
                            ].copy()
                            top5['Failure_Probability'] = (top5['Failure_Probability']*100).round(1).astype(str) + '%'
                            top5['Utilization']         = (top5['Utilization']*100).round(1).astype(str) + '%'
                            st.dataframe(top5, use_container_width=True, hide_index=True)

                            csv_out = result.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="⬇️ Download Pipe Results CSV",
                                data=csv_out,
                                file_name="pipe_evaluation_results.csv",
                                mime="text/csv",
                                key='pipe_download'
                            )
                        except Exception as e:
                            st.error(f"Analysis failed: {str(e)}")
        except Exception as e:
            st.error(f"Could not read file: {str(e)}")

# ── Footer ────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#37474f;font-size:0.78rem;padding:1rem;border-top:1px solid #1e2130;">
    Urban Drainage Network Analyzer • Physics Engine + Random Forest ML • Seattle SPU Dataset
</div>
""", unsafe_allow_html=True)
