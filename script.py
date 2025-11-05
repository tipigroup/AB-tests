import streamlit as st
import numpy as np
from scipy import stats

st.set_page_config(page_title="A/B Test", layout="wide")

# Custom CSS for colored headers
st.markdown("""
<style>
.section-header {
    padding: 10px;
    color: white;
    font-weight: bold;
    text-align: center;
    margin-bottom: 10px;
    border-radius: 5px;
}
.blue-header {
    background-color: #1e5a7d;
}
.green-header {
    background-color: #4a8c2a;
}
.orange-header {
    background-color: #d87035;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="section-header blue-header">AB TEST</div>', unsafe_allow_html=True)

# Create two columns for main layout
main_col1, main_col2 = st.columns([1, 1], gap="medium")

# LEFT COLUMN - Sample Size RequiredF
with main_col1:
    st.markdown('<div class="section-header blue-header">Sample size required for the test</div>', unsafe_allow_html=True)
    
    kpi_base = st.number_input(
        "Current Base KPI (Example Conversion Rate) %",
        min_value=0.01, max_value=100.0,
        value=12.0, step=0.1,
        key="kpi_base"
    )
    
    mde = st.number_input(
        "Expected Increase - Minimum Detectable Effect (MDE) %",
        min_value=0.01, max_value=500.0, value=16.0, step=0.1,
        key="mde"
    )
    
    c1, c2 = st.columns(2)
    c1.metric("Base KPI", f"{kpi_base:.2f}%")
    c2.metric("Expected KPI", f"{(kpi_base/100 * (1+mde/100))*100:.2f}%")
    
    
    # Convert to decimals
    p1 = kpi_base / 100.0
    mde_decimal = mde / 100.0
    p2 = p1 * (1 + mde_decimal)
    delta = abs(p2 - p1)
    
    # Get alpha and power from session state (will be set in right column)
    if 'alpha_percent' not in st.session_state:
        st.session_state.alpha_percent = 5.0
    if 'power_percent' not in st.session_state:
        st.session_state.power_percent = 80.0
    
    alpha = st.session_state.alpha_percent / 100.0
    power = st.session_state.power_percent / 100.0
    
    # Sample size calculation
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
    
    # Compute sample size
    n_two = pooled_sample_size(p1, p2, alpha, power, tails="two")
    
    res_col1, res_col2 = st.columns(2)
    res_col1.metric("Sample Size per Group", f"{n_two:,}")
    res_col2.metric("Total Sample Size", f"{n_two * 2:,}")
    
    st.markdown("---")
    
    # Budget Required Section
    st.markdown('<div class="section-header blue-header">Budget required for the test</div>', unsafe_allow_html=True)
        
    forecast_impressions = st.number_input(
        "Forecast Impression Sample Size",
        min_value=0,
        value=n_two * 2,
        step=1000,
        help="Estimate of how many impressions will be served per person. Default is one impression served per person",
        key="forecast_impressions"
    )
    
    price_per_1000 = st.number_input(
        "CPM",
        min_value=0.0,
        value=5.0,
        step=0.1,
        key="cpm"
    )
        
    # Calculate costs
    total_cost = (forecast_impressions / 1000) * price_per_1000
    cost_per_group = total_cost / 2
    
    cost_col1, cost_col2, descriptor = st.columns(3)
    cost_col1.metric("Total Campaign Cost", f"${total_cost:,.2f}")
    cost_col2.metric("Cost per Group", f"${cost_per_group:,.2f}")
    descriptor.metric("Minimum Duration", "4-6 Weeks")

# RIGHT COLUMN - Budget Required and Other Stats
with main_col2:
    # Other stat stuff section
    st.markdown('<div class="section-header orange-header">Statistical Settings</div>', unsafe_allow_html=True)
    
    st.markdown("These settings have been applied as a default, check with the data for any changes")
    
    alpha_percent = st.number_input(
        "Significance level %",
        min_value=0.1, max_value=20.0, value=5.0, step=0.1,
        key="alpha_input"
    )
    st.session_state.alpha_percent = alpha_percent
    
    power_percent = st.number_input(
        "Power %",
        min_value=50.0, max_value=99.9, value=80.0, step=1.0,
        key="power_input"
    )
    st.session_state.power_percent = power_percent

# Bottom Section - Calculations and Models (full width)
st.markdown("---")
st.markdown('<div class="section-header blue-header">Calculations and models</div>', unsafe_allow_html=True)

effect_size_h = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))

with st.expander("Calculation details (formulas)", expanded=False):
    st.markdown(f"""
**Parameters:**
- p₁ = {p1:.6f}  
- p₂ = {p2:.6f}  
- Δ = |p₂ - p₁| = {delta:.6f}  
- pooled p̄ = (p₁ + p₂)/2 = {(p1+p2)/2:.6f}  

**Pooled formula used (per-group):**

n = 2 × (Z_crit + Z_β)² × p̄ (1 − p̄) / Δ²  

**Where:**  
- Z_crit = Z₁₋α/₂ (two-tailed) or Z₁₋α (one-tailed)  
- Z_β = Z_power  

**Examples with current inputs:**  
- Two-tailed → Z_crit = {stats.norm.ppf(1 - alpha/2):.6f}, Z_β = {stats.norm.ppf(power):.6f} → n = {n_two:,}

**Effect Size (Cohen's h):** {effect_size_h:.6f}
""")