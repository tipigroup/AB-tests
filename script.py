import streamlit as st
import numpy as np
from scipy import stats

st.set_page_config(page_title="A/B Test Power Analysis (Pooled)", layout="wide")
st.title("A/B Test Power Analysis Calculator")

col1, col2 = st.columns([1,1], gap="small")

with col1:
    st.subheader("🟩 Input Parameters")
    kpi_base = st.number_input(
        "Current Base KPI (Example Conversion Rate) %",
        min_value=0.01, max_value=100.0,
        value=12.0, step=0.1,
    )
    mde = st.number_input(
        "Expected Increase - Minimum Detectable Effect (MDE) %",
        min_value=0.01, max_value=500.0, value=16.0, step=0.1,
    )
    c1, c2 = st.columns(2)
    c1.metric("Base KPI", f"{kpi_base:.2f}%")
    c2.metric("Expected KPI", f"{(kpi_base/100 * (1+mde/100))*100:.2f}%")

with col2:
    with st.expander("🔴 Statistical Settings", expanded=False):
        st.markdown("These settings have been applied as a default, check with the data for any changes")
        
        alpha_percent = st.number_input(
            "Significance level %",
            min_value=0.1, max_value=20.0, value=5.0, step=0.1
        )
        power_percent = st.number_input(
            "Power %",
            min_value=50.0, max_value=99.9, value=80.0, step=1.0
        )

# Convert to decimals
p1 = kpi_base / 100.0
mde_decimal = mde / 100.0
p2 = p1 * (1 + mde_decimal)
delta = abs(p2 - p1)
alpha = alpha_percent / 100.0
power = power_percent / 100.0

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

# Output
st.markdown("---")
st.subheader("Required Sample Size")
res_col1, res_col2 = st.columns(2)
res_col1.metric(
    "Sample Size",
    f"{n_two:,}",
)

res_col2.metric(
    "Total Sample Size",
    f"{n_two * 2:,}"
)

# Forecast and Cost Section
st.markdown("---")
st.subheader("Forecast & Cost Analysis")
forecast_col1, forecast_col2 = st.columns(2)

with forecast_col1:
    forecast_impressions = st.number_input(
        "Forecast Impression Sample Size",
        min_value=0,
        value=n_two * 2,
        step=1000,
    )

with forecast_col2:
    price_per_1000 = st.number_input(
        "Price per 1,000 Impressions",
        min_value=0.0,
        value=5.0,
        step=0.1,
    )

# Calculate costs
total_cost = (forecast_impressions / 1000) * price_per_1000
cost_per_group = total_cost / 2

# Display cost metrics
cost_col1, cost_col2, cost_col3 = st.columns(3)
cost_col1.metric(
    "Total Campaign Cost",
    f"{total_cost:,.2f}"
)
cost_col2.metric(
    "Cost per Group",
    f"{cost_per_group:,.2f}"
)
cost_col3.metric(
    "CPM",
    f"{price_per_1000:.2f}"
)


# Effect size
st.markdown("---")
st.subheader("Calculations and models")
effect_size_h = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))

with st.expander("Calculation details (formulas)"):
    st.markdown(f"""
- p₁ = {p1:.6f}  
- p₂ = {p2:.6f}  
- Δ = |p₂ - p₁| = {delta:.6f}  
- pooled p̄ = (p₁ + p₂)/2 = {(p1+p2)/2:.6f}  

**Pooled formula used (per-group):**

n = 2 × (Z_crit + Z_β)² × p̄ (1 − p̄) / Δ²  

Where:  
- Z_crit = Z₁₋α/₂ (two-tailed) or Z₁₋α (one-tailed)  
- Z_β = Z_{power}  

Examples with current inputs:  
- Two-tailed → Z_crit = {stats.norm.ppf(1 - alpha/2):.6f}, Z_β = {stats.norm.ppf(power):.6f} → n = {n_two:,}
""")
