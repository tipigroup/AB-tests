import streamlit as st
import numpy as np
from scipy import stats

st.set_page_config(page_title="ROAST A/B Test Calculator", layout="wide")

# Custom CSS for ROAST branding
st.markdown("""
<style>
/* ROAST Brand Colors */
:root {
    --roast-primary: #FF6B35;
    --roast-dark: #1a1a1a;
    --roast-light: #f5f5f5;
    --roast-accent: #00D9FF;
    --roast-grey: #666666;
}

/* Main container styling */
.main {
    background-color: #ffffff;
}

/* Section headers */
.section-header {
    padding: 15px 20px;
    color: white;
    font-weight: 700;
    text-align: center;
    margin-bottom: 20px;
    border-radius: 0px;
    font-size: 1.1em;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.roast-primary-header {
    background-color: #FF6B35;
}

.roast-dark-header {
    background-color: #1a1a1a;
}

.roast-accent-header {
    background-color: #00D9FF;
    color: #1a1a1a;
}

/* Metric styling */
.stMetric {
    background-color: #000000;
    padding: 5px;
    border-radius: 0px;
    border-left: 4px solid #FF6B35;
}

/* Input styling */
.stNumberInput > div > div > input {
    border-radius: 0px;
    border: 2px solid #e0e0e0;
}

.stNumberInput > div > div > input:focus {
    border-color: #FF6B35;
    box-shadow: 0 0 0 0.2rem rgba(255, 107, 53, 0.15);
}

/* Expander styling */
.streamlit-expanderHeader {
    background-color: #f8f8f8;
    border-radius: 0px;
    border-left: 4px solid #00D9FF;
    font-weight: 600;
}

/* Divider */
hr {
    border-color: #FF6B35;
    border-width: 2px;
}
</style>
""", unsafe_allow_html=True)

# Logo and title
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("roast.png", width=120)
    except:
        st.markdown("### 🔥 ROAST")

with col_title:
    st.markdown('<div class="section-header roast-dark-header">A/B TEST CALCULATOR</div>', unsafe_allow_html=True)

# Create two columns for main layout
main_col1, main_col2 = st.columns([1, 1], gap="large")

# LEFT COLUMN - Sample Size Required
with main_col1:
    st.markdown('<div class="section-header roast-primary-header">Sample Size Required for the Test</div>', unsafe_allow_html=True)
    
    kpi_base = st.number_input(
        "Current Base KPI (Example: Conversion Rate) %",
        min_value=0.01, max_value=100.0,
        value=12.0, step=0.1,
        key="kpi_base",
    )
    
    mde = st.number_input(
        "Expected Increase - Minimum Detectable Effect (MDE) %",
        min_value=0.01, max_value=500.0, value=16.0, step=0.1,
        key="mde",
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
    st.markdown('<div class="section-header roast-primary-header">Budget Required for the Test</div>', unsafe_allow_html=True)
        
    forecast_impressions = st.number_input(
        "Forecast Impression Sample Size",
        min_value=0,
        value=n_two * 2,
        step=1000,
        help="Estimate of how many impressions will be served. Default is one impression per person",
        key="forecast_impressions"
    )
    
    price_per_1000 = st.number_input(
        "CPM",
        min_value=0.0,
        value=5.0,
        step=0.1,
        key="cpm",
    )
        
    # Calculate costs
    total_cost = (forecast_impressions / 1000) * price_per_1000
    cost_per_group = total_cost / 2
    
    cost_col1, cost_col2, descriptor = st.columns(3)
    cost_col1.metric("Total Campaign Cost", f"${total_cost:,.2f}")
    cost_col2.metric("Cost per Group", f"${cost_per_group:,.2f}")
    descriptor.metric("Minimum Duration", "4-6 Weeks")

# RIGHT COLUMN - Statistical Settings
with main_col2:
    st.markdown('<div class="section-header roast-accent-header">Statistical Settings</div>', unsafe_allow_html=True)
    
    st.info("These settings have been applied as defaults. Check with the data for any changes.")
    
    alpha_percent = st.number_input(
        "Significance Level %",
        min_value=0.1, max_value=20.0, value=5.0, step=0.1,
        key="alpha_input",
    )
    st.session_state.alpha_percent = alpha_percent
    
    power_percent = st.number_input(
        "Power %",
        min_value=50.0, max_value=99.9, value=80.0, step=1.0,
        key="power_input",
    )
    st.session_state.power_percent = power_percent
    
    st.markdown("---")
    
    # Key Insights Section
    
 
    
# Bottom Section - Calculations and Models (full width)
st.markdown("---")
st.markdown('<div class="section-header roast-dark-header">Technical Details & Formulas</div>', unsafe_allow_html=True)

with st.expander("Calculation methodology", expanded=False):
    effect_size_h = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))
    st.markdown(f"""
    ### Statistical Parameters
    
    **Proportions:**
    - p₁ (Control) = {p1:.6f}  
    - p₂ (Test) = {p2:.6f}  
    - Δ (Absolute Difference) = |p₂ - p₁| = {delta:.6f}  
    - p̄ (Pooled Proportion) = (p₁ + p₂)/2 = {(p1+p2)/2:.6f}  
    
    ### Sample Size Formula (Pooled Method)
    
    The sample size per group is calculated using:
    
    ```
    n = 2 × (Z_α/2 + Z_β)² × p̄(1 - p̄) / Δ²
    ```
    
    **Where:**  
    - **Z_α/2** = Critical value for two-tailed test at significance level α
    - **Z_β** = Critical value for desired statistical power (1-β)
    - **p̄** = Pooled proportion
    - **Δ** = Absolute difference between proportions
    
    ### Current Calculation
    
    - Significance level (α) = {alpha_percent:.1f}% → Z_α/2 = {stats.norm.ppf(1 - alpha/2):.4f}
    - Statistical power = {power_percent:.1f}% → Z_β = {stats.norm.ppf(power):.4f}
    - **Sample size per group (n)** = **{n_two:,}**
    - **Total sample size** = **{n_two * 2:,}**
    
    ### Effect Size Metrics
    
    **Cohen's h** = 2 × [arcsin(√p₂) - arcsin(√p₁)] = **{effect_size_h:.4f}**
    
    *Cohen's h interpretation:*
    - Small effect: h ≈ 0.2
    - Medium effect: h ≈ 0.5  
    - Large effect: h ≈ 0.8
    
    ### Test Duration Recommendation
    
    For reliable results, run your test for **at least 4-6 weeks** to account for:
    - Weekly seasonality patterns
    - Sufficient sample collection
    - Statistical maturation effects
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666666; padding: 20px;'>
    <p><strong>ROAST Performance Media</strong> | A/B Test Calculator</p>
    <p style='font-size: 0.9em;'>For support or questions about this program, contact the tooling team.</p>
</div>
""", unsafe_allow_html=True)