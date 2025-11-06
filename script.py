import streamlit as st
import numpy as np
from scipy import stats

st.set_page_config(page_title="ROAST A/B Test Calculator", layout="wide")

# =========================
# Custom CSS Styling
# =========================
st.markdown("""
<style>
:root {
    --roast-primary: #FF6B35;
    --roast-dark: #1a1a1a;
    --roast-light: #f5f5f5;
    --roast-accent: #FFD700;
    --roast-grey: #666666;
}
.main { background-color: #f8f9fa; }
.metric-card {
    background: white; border-radius: 8px; padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;
    border-left: 4px solid #FFD700;
}
.metric-card-primary { border-left-color: #FF6B35; }
.metric-card-accent { border-left-color: #00D9FF; }
.section-header {
    font-size: 1.5em; font-weight: 700; color: #1a1a1a;
    margin-bottom: 20px; padding-bottom: 10px;
}
.metric-value {
    font-size: 2.5em; font-weight: 700; color: #1a1a1a; line-height: 1.2;
}
.metric-label {
    font-size: 0.9em; color: #666666; margin-top: 5px;
    text-transform: uppercase; letter-spacing: 0.5px;
}
.metric-sublabel { font-size: 0.85em; color: #999999; margin-top: 3px; }
.yellow-badge {
    background-color: #FFD700; color: #1a1a1a; padding: 4px 12px;
    border-radius: 4px; font-size: 0.85em; font-weight: 600;
    display: inline-block; margin-bottom: 15px;
}
.analysis-section {
    background: white; border-radius: 10px; padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-top: 35px;
    margin-bottom: 25px;
    font-size: 2em; color: #1a1a1a;
}
.stButton > button {
    background-color: #1a1a1a; color: white; border-radius: 4px;
    padding: 10px 30px; font-weight: 600; border: none;
}
.stButton > button:hover { background-color: #FF6B35; }
.stNumberInput > div > div > input {
    border-radius: 4px; border: 1px solid #ddd;
}
.stNumberInput > div > div > input:focus {
    border-color: #FF6B35;
    box-shadow: 0 0 0 0.2rem rgba(255, 107, 53, 0.15);
}
.info-box {
    background-color: #e8f4f8; border-left: 4px solid #00D9FF;
    padding: 15px; border-radius: 4px; margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# INPUT SECTION AT TOP
# =========================
st.markdown("## ⚙️ Input Controls")
st.markdown("---")

# Layout for inputs
input_col1, input_col2, input_col3, input_col4 = st.columns([2, 2, 2, 2])

with input_col1:
    kpi_base = st.number_input(
        "Base KPI (Conversion Rate) %",
        min_value=0.01, max_value=100.0,
        value=12.0, step=0.1, key="kpi_base"
    )

with input_col2:
    mde = st.number_input(
        "Minimum Detectable Effect (MDE) %",
        min_value=0.01, max_value=500.0,
        value=16.0, step=0.1, key="mde"
    )

with input_col3:
    price_per_1000 = st.number_input(
        "CPM",
        min_value=0.0, value=5.0,
        step=0.1, key="cpm"
    )

with input_col4:
    forecast_impressions = st.number_input(
        "Forecasted Impressions",
        min_value=0.0, value=100000.0,
        step=1000.0, key="forecast_impressions"
    )

# Statistical settings (below inputs)
settings_col1, settings_col2, settings_col3 = st.columns(3)

with settings_col1:
    alpha_percent = st.number_input(
        "Significance Level (%)",
        min_value=0.1, max_value=20.0, value=5.0, step=0.1,
        key="alpha_input"
    )

with settings_col2:
    power_percent = st.number_input(
        "Statistical Power (%)",
        min_value=50.0, max_value=99.9, value=80.0, step=1.0,
        key="power_input"
    )

with settings_col3:
    st.metric("Recommended Duration", "4–6 Weeks",)

# =========================
# CALCULATIONS
# =========================
p1 = kpi_base / 100.0
mde_decimal = mde / 100.0
p2 = p1 * (1 + mde_decimal)
delta = abs(p2 - p1)
alpha = alpha_percent / 100.0
power = power_percent / 100.0

def pooled_sample_size(p1, p2, alpha, power, tails="two"):
    if tails == "two":
        z_alpha = stats.norm.ppf(1 - alpha / 2.0)
    else:
        z_alpha = stats.norm.ppf(1 - alpha)
    z_beta = stats.norm.ppf(power)
    pbar = (p1 + p2) / 2.0
    delta = abs(p2 - p1)
    n = 2.0 * (z_alpha + z_beta) ** 2 * pbar * (1 - pbar) / (delta ** 2)
    return int(np.ceil(n))

n_two = pooled_sample_size(p1, p2, alpha, power)
total_cost = (forecast_impressions / 1000) * price_per_1000
cost_per_group = total_cost / 2

# =========================
# RESULTS: METRICS
# =========================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="yellow-badge">📈 KEY METRICS</div>', unsafe_allow_html=True)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{n_two:,}</div>
        <div class="metric-label">Sample per Group</div>
        <div class="metric-sublabel">Required for significance</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{n_two * 2:,}</div>
        <div class="metric-label">Total Sample Size</div>
        <div class="metric-sublabel">Combined A/B groups</div>
    </div>
    """, unsafe_allow_html=True)

with metric_col3:
    expected_kpi = (p1 * (1 + mde_decimal)) * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{expected_kpi:.2f}%</div>
        <div class="metric-label">Expected KPI</div>
        <div class="metric-sublabel">Target conversion rate</div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# BUDGET ANALYSIS
# =========================
st.markdown('<div class="analysis-section">Budget Analysis</div>', unsafe_allow_html=True)

cost_col1, cost_col2 = st.columns(2)

with cost_col1:
    st.markdown(f"""
    <div class="metric-card metric-card-primary">
        <div class="metric-value" style="font-size: 2em;">${total_cost:,.2f}</div>
        <div class="metric-label">Total Campaign Cost</div>
    </div>
    """, unsafe_allow_html=True)

with cost_col2:
    st.markdown(f"""
    <div class="metric-card metric-card-primary">
        <div class="metric-value" style="font-size: 2em;">${cost_per_group:,.2f}</div>
        <div class="metric-label">Cost per Group</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# TECHNICAL DETAILS
# =========================
with st.expander("📐 Technical Details & Formulas", expanded=False):
    effect_size_h = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))
    st.markdown(f"""
    ### Statistical Parameters
    
    **Proportions:**
    - p₁ (Control) = {p1:.6f}  
    - p₂ (Test) = {p2:.6f}  
    - Δ (Absolute Difference) = |p₂ - p₁| = {delta:.6f}  
    - p̄ (Pooled Proportion) = {(p1 + p2) / 2:.6f}  
    
    ### Sample Size Formula (Pooled Method)
    ```
    n = 2 × (Z_α/2 + Z_β)² × p̄(1 - p̄) / Δ²
    ```
    - α = {alpha_percent:.1f}% → Z_α/2 = {stats.norm.ppf(1 - alpha/2):.4f}
    - Power = {power_percent:.1f}% → Z_β = {stats.norm.ppf(power):.4f}
    - n per group = {n_two:,}
    - Total n = {n_two * 2:,}
    - Cohen’s h = {effect_size_h:.4f}
    """)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666666; padding: 20px;'>
    <p><strong>ROAST Performance Media</strong> | A/B Test Calculator</p>
    <p style='font-size: 0.9em;'>For support or questions about this tool, contact the analytics team.</p>
</div>
""", unsafe_allow_html=True)
