import streamlit as st
import numpy as np
from scipy import stats

st.set_page_config(page_title="A/B Test Power Analysis (Pooled)", layout="wide")
st.title("A/B Test Power Analysis Calculator")

# Custom CSS for color-coding sections
st.markdown("""
<style>
.green-box {
    background-color: #e6ffe6;
    border-left: 5px solid #00cc00;
    padding: 10px;
    border-radius: 10px;
}
.red-box {
    background-color: #ffe6e6;
    border-left: 5px solid #ff0000;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🟩 Input Parameters")
    kpi_base = st.number_input(
        "Current Base KPI (Example Conversion Rate) %",
        min_value=0.001, max_value=100.0,
        value=12.0, step=0.1,
        help="Baseline conversion rate as a percentage (e.g. 12 for 12%)."
    )
    mde = st.number_input(
        "Expected Increase - Minimum Detectable Effect (MDE) %",
        min_value=0.1, max_value=500.0, value=16.0, step=0.1,
        help="Relative percent increase you want to detect (e.g. 16 for +16%)."
    )
    c1, c2 = st.columns(2)
    c1.metric("Control rate", f"{kpi_base:.2f}%")
    c2.metric("Variant rate", f"{(kpi_base/100 * (1+mde/100))*100:.2f}%")

with col2:
    with st.expander("🔴 Statistical Settings", expanded=False):
        st.markdown("These settings have been applied as a default, they are not intended to be changed")
        
        alpha_percent = st.number_input(
            "Significance level %",
            min_value=0.1, max_value=20.0, value=5.0, step=0.1
        )
        power_percent = st.number_input(
            "Power",
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
    help=f"Two-tailed α={alpha_percent}% power={power_percent}%"
)

res_col2.metric(
    "Total Sample Size",
    f"{n_two * 2:,}"
)

# Effect size
st.markdown("---")
st.subheader("Selected Result")
effect_size_h = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))
st.markdown(f"**Effect size (Cohen's h):** {effect_size_h:.4f}")

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
