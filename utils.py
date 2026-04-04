import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import streamlit as st

# ── Config ────────────────────────────────────────────────────────────
MAP_WEBSITE_URL = "https://your-mapping-website.streamlit.app"  # 🔁 Replace after deployment

DRAIN_REQUIRED_COLS = [
    'Drain_ID', 'Rainfall_mm_hr', 'Catchment_km2',
    'Impervious_frac', 'Runoff_coeff', 'Design_Capacity_m3hr',
]
PIPE_REQUIRED_COLS = [
    'Pipe_ID', 'Diameter_in', 'Slope_pct', 'Material', 'Install_Date'
]

# ── Shared CSS ────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }
.main { background-color: #0a0e1a !important; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0e1a 100%) !important;
    border-right: 1px solid #1e2440;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1400px; }

/* Glassmorphism card */
.glass-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
}
.glass-card:hover { border-color: rgba(41,121,255,0.3); box-shadow: 0 8px 32px rgba(13,71,161,0.2); }

/* Stat cards */
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 1.2rem;
    text-align: center; transition: all 0.3s;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.stat-card:hover { transform: translateY(-2px); border-color: rgba(41,121,255,0.4); }
.stat-number { font-size: 2rem; font-weight: 700; color: #ffffff; line-height: 1; }
.stat-label  { font-size: 0.72rem; color: #64748b; margin-top: 0.4rem; text-transform: uppercase; letter-spacing: 0.08em; }
.stat-safe     .stat-number { color: #4ade80; }
.stat-stressed .stat-number { color: #fb923c; }
.stat-critical .stat-number { color: #f87171; }

/* Highlight card */
.risk-card {
    background: linear-gradient(135deg, rgba(239,83,80,0.12), rgba(183,28,28,0.08));
    border: 1px solid rgba(239,83,80,0.35);
    border-radius: 14px; padding: 1.2rem 1.5rem; margin: 1rem 0;
    box-shadow: 0 0 20px rgba(239,83,80,0.1);
}
.risk-card-title { color: #f87171; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
.risk-card-id    { color: #ffffff; font-size: 1.2rem; font-weight: 700; }
.risk-card-meta  { color: #94a3b8; font-size: 0.82rem; margin-top: 0.4rem; }
.risk-card-meta strong { color: #fca5a5; }

/* Status badges */
.badge { display: inline-block; padding: 0.2rem 0.7rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-safe     { background: rgba(74,222,128,0.12); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
.badge-stressed { background: rgba(251,146,60,0.12); color: #fb923c; border: 1px solid rgba(251,146,60,0.3); }
.badge-critical { background: rgba(248,113,113,0.12); color: #f87171; border: 1px solid rgba(248,113,113,0.3); }

/* Error/Success boxes */
.error-box {
    background: rgba(183,28,28,0.15); border: 1px solid rgba(239,83,80,0.4);
    border-radius: 10px; padding: 1rem 1.2rem; margin: 0.8rem 0;
}
.error-box h4 { color: #f87171; margin: 0 0 0.5rem 0; font-size: 0.9rem; }
.error-box ul  { color: #fca5a5; margin: 0; padding-left: 1.2rem; font-size: 0.85rem; }
.success-box {
    background: rgba(20,83,45,0.2); border: 1px solid rgba(74,222,128,0.3);
    border-radius: 10px; padding: 0.8rem 1.2rem; margin: 0.8rem 0;
}
.success-box p { color: #86efac; margin: 0; font-size: 0.88rem; }

/* Required cols */
.req-cols {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 1rem;
    font-size: 0.78rem; color: #64748b;
}
.req-cols strong { color: #7dd3fc; }
.req-cols code { background: rgba(41,121,255,0.1); color: #93c5fd; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.75rem; }

/* Section headers */
.section-header { color: #e2e8f0; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.2rem; }
.section-sub    { color: #475569; font-size: 0.82rem; margin-bottom: 1.2rem; }

/* Divider */
.divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 1.2rem 0; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 10px !important; padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important; width: 100% !important;
    transition: all 0.2s !important; letter-spacing: 0.02em !important;
    box-shadow: 0 4px 14px rgba(29,78,216,0.35) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.45) !important;
}

/* Sidebar nav */
.nav-item {
    padding: 0.6rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;
    cursor: pointer; transition: all 0.2s; font-size: 0.88rem;
    color: #64748b; border: 1px solid transparent;
}
.nav-item:hover   { background: rgba(255,255,255,0.05); color: #e2e8f0; }
.nav-item.active  { background: rgba(29,78,216,0.2); color: #93c5fd; border-color: rgba(29,78,216,0.3); }

/* Dataframe */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Page title */
.page-title {
    background: linear-gradient(135deg, rgba(13,71,161,0.3), rgba(29,78,216,0.15));
    border: 1px solid rgba(41,121,255,0.2); border-radius: 16px;
    padding: 1.5rem 2rem; margin-bottom: 2rem;
    border-left: 4px solid #2979ff;
}
.page-title h1 { color: #ffffff; margin: 0; font-size: 1.6rem; font-weight: 700; }
.page-title p  { color: #64748b; margin: 0.3rem 0 0 0; font-size: 0.88rem; }

/* Map banner */
.map-banner {
    background: linear-gradient(135deg, rgba(13,33,55,0.8), rgba(10,61,98,0.6));
    border: 1px solid rgba(21,101,192,0.4); border-radius: 12px;
    padding: 1rem 1.5rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.map-banner h3 { color: #7dd3fc; margin: 0; font-size: 0.95rem; font-weight: 600; }
.map-banner p  { color: #475569; margin: 0.2rem 0 0 0; font-size: 0.78rem; }
.map-btn a {
    background: linear-gradient(135deg, #1d4ed8, #1e40af);
    color: #ffffff !important; text-decoration: none;
    padding: 0.5rem 1.2rem; border-radius: 8px; font-weight: 600;
    font-size: 0.82rem; white-space: nowrap; border: 1px solid rgba(41,121,255,0.5);
    box-shadow: 0 2px 8px rgba(29,78,216,0.3);
}

/* Tooltip */
.tooltip { position: relative; display: inline-block; border-bottom: 1px dotted #475569; cursor: help; }
.tooltip .tip {
    visibility: hidden; background: #1e293b; color: #94a3b8;
    text-align: center; border-radius: 6px; padding: 0.4rem 0.8rem;
    position: absolute; z-index: 1; bottom: 125%; left: 50%;
    transform: translateX(-50%); white-space: nowrap; font-size: 0.75rem;
    border: 1px solid rgba(255,255,255,0.1);
}
.tooltip:hover .tip { visibility: visible; }

/* Plotly chart backgrounds */
.js-plotly-plot { border-radius: 12px; }

/* Hide streamlit default elements */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
"""

# ── Helper functions ──────────────────────────────────────────────────

def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def check_columns(df, required):
    return [c for c in required if c not in df.columns]

def get_degradation_col(df):
    if 'Degradation_Factor' in df.columns:   return 'Degradation_Factor'
    if 'Degradation_Factor_x' in df.columns: return 'Degradation_Factor_x'
    return None

def status_badge(status):
    cls = {'SAFE':'safe','STRESSED':'stressed','CRITICAL':'critical'}.get(status,'safe')
    return f'<span class="badge badge-{cls}">{status}</span>'

def show_stat_cards(df, status_col, prob_col):
    total    = len(df)
    safe     = (df[status_col]=='SAFE').sum()
    stressed = (df[status_col]=='STRESSED').sum()
    critical = (df[status_col]=='CRITICAL').sum()
    avg_prob = df[prob_col].mean()*100
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total}</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card stat-safe"><div class="stat-number">{safe}</div><div class="stat-label">Safe</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card stat-stressed"><div class="stat-number">{stressed}</div><div class="stat-label">Stressed</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card stat-critical"><div class="stat-number">{critical}</div><div class="stat-label">Critical</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{avg_prob:.1f}%</div><div class="stat-label">Avg Risk</div></div>', unsafe_allow_html=True)

# ── Analysis functions (exact logic from app.py) ──────────────────────

def run_drain_analysis(df):
    df = df.copy()
    deg_col = get_degradation_col(df)
    df['Q_runoff']          = df['Rainfall_mm_hr'] * df['Catchment_km2'] * df['Runoff_coeff'] * 100
    df['Q_baseflow']        = 5 * df['Catchment_km2'] * df['Impervious_frac']
    df['Q_total_in']        = df['Q_runoff'] + df['Q_baseflow']
    df['Q_eff']             = df['Design_Capacity_m3hr'] * df[deg_col]
    df['Utilization_Ratio'] = df.apply(lambda r: r['Q_total_in']/r['Q_eff'] if r['Q_eff']!=0 else 0, axis=1)

    def get_status(u):
        if u < 0.6:    return 'SAFE'
        elif u <= 0.9: return 'STRESSED'
        else:          return 'CRITICAL'

    df['Operational_Status'] = df['Utilization_Ratio'].apply(get_status)
    status_to_label = {'SAFE':0,'STRESSED':1,'CRITICAL':2}
    df['Status_Label'] = df['Operational_Status'].map(status_to_label)

    features = ['Rainfall_mm_hr','Impervious_frac',deg_col,'Catchment_km2','Runoff_coeff']
    if 'Slope' in df.columns: features.insert(1,'Slope')
    features = [f for f in features if f in df.columns]

    X        = df[features].fillna(0)
    y        = df['Status_Label']
    scaler   = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    probs     = model.predict_proba(X_scaled)
    n_classes = probs.shape[1]
    if n_classes==3:   df['Failure_Probability'] = probs[:,1]+probs[:,2]
    elif n_classes==2: df['Failure_Probability'] = probs[:,1]
    else:              df['Failure_Probability'] = 1-probs[:,0]
    return df

def run_pipe_analysis(df):
    def parse_year(val):
        if pd.isna(val): return np.nan
        try: return int(str(val)[:4]) if str(val)[:4].isdigit() else pd.to_datetime(val).year
        except: return np.nan

    pipes = df.copy()
    pipes['Install_Year'] = pipes['Install_Date'].apply(parse_year)
    pipes['Pipe_Age']     = 2026 - pipes['Install_Year']
    pipes['Pipe_Age']     = pipes['Pipe_Age'].fillna(pipes['Pipe_Age'].median())
    pipes['Slope_pct']    = pipes['Slope_pct'].fillna(pipes['Slope_pct'].median())
    roughness_map = {
        'Concrete':0.013,'Reinforced Concrete Pipe':0.013,'Vitrified Clay':0.014,
        'Cast Iron Pipe':0.015,'Ductile Iron Pipe':0.012,'Polyvinyl Chloride':0.009,
        'High Density Polyethylene':0.011,'Brick':0.016,'Asbestos Cement':0.011,'Unknown':0.013,
    }
    pipes['Roughness_n']      = pipes['Material'].map(roughness_map).fillna(0.013)
    pipes['Diameter_m']       = pipes['Diameter_in']*0.0254
    pipes['Area_m2']          = np.pi*(pipes['Diameter_m']/2)**2
    pipes['Hydraulic_Radius'] = pipes['Diameter_m']/4
    pipes['Slope_safe']       = pipes['Slope_pct'].clip(lower=0.01)/100
    pipes['Capacity_m3_s']    = (1/pipes['Roughness_n'])*pipes['Area_m2']*(pipes['Hydraulic_Radius']**(2/3))*(pipes['Slope_safe']**0.5)

    def degradation(row):
        age,mat = row['Pipe_Age'],row['Material']
        if mat in ['Vitrified Clay','Brick','Asbestos Cement','Cast Iron Pipe']: return max(0.3,1-age*0.008)
        elif mat in ['Concrete','Reinforced Concrete Pipe']:                      return max(0.4,1-age*0.006)
        else:                                                                      return max(0.6,1-age*0.003)

    pipes['Degradation_Factor'] = pipes.apply(degradation,axis=1)
    pipes['Effective_Capacity'] = pipes['Capacity_m3_s']*pipes['Degradation_Factor']
    np.random.seed(42)
    pipes['Pipe_Flow_m3_s'] = (pipes['Effective_Capacity']*(0.4+0.5*(pipes['Pipe_Age']/pipes['Pipe_Age'].max()))+np.random.normal(0,0.05,len(pipes))).clip(lower=0)
    pipes['Utilization']    = pipes['Pipe_Flow_m3_s']/pipes['Effective_Capacity'].replace(0,np.nan)

    def classify(u):
        if u<0.6: return 0
        elif u<0.9: return 1
        else: return 2

    pipes['Pipe_Status_Label'] = pipes['Utilization'].apply(classify)
    pipes['Pipe_Status']       = pipes['Pipe_Status_Label'].map({0:'SAFE',1:'STRESSED',2:'CRITICAL'})
    features = [f for f in ['Diameter_in','Pipe_Age','Slope_pct','Utilization','Degradation_Factor','Roughness_n'] if f in pipes.columns]
    X        = pipes[features].fillna(0)
    y        = pipes['Pipe_Status_Label']
    scaler   = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    X_train,X_test,y_train,y_test = train_test_split(X_scaled,y,test_size=0.2,random_state=42)
    model = RandomForestClassifier(n_estimators=200,max_depth=8,random_state=42)
    model.fit(X_train,y_train)
    probs     = model.predict_proba(X_scaled)
    n_classes = probs.shape[1]
    if n_classes==3:   pipes['Failure_Probability'] = probs[:,1]+probs[:,2]
    elif n_classes==2: pipes['Failure_Probability'] = probs[:,1]
    else:              pipes['Failure_Probability'] = 1-probs[:,0]
    pipes['Pipe_Status'] = pipes['Pipe_Status_Label'].map({0:'SAFE',1:'STRESSED',2:'CRITICAL'})
    return pipes
