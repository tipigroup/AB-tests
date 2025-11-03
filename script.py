import streamlit as st
import numpy as np
from scipy import stats

st.set_page_config(page_title="A/B Test Power Analysis (Pooled)", layout="wide")

st.title("A/B Test Power Analysis Calculator — Pooled formula (Optimizely-style)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Parameters")
    kpi_base = st.number_input(
        "Current KPI (Conversion Rate) %", min_value=0.001, max_value=100.0,
        value=12.0, step=0.1, help="Baseline conversion rate as a percentage (e.g. 12 for 12%)."
    )
    mde = st.number_input(
        "Minimum Detectable Effect (MDE) % (relative)",
        min_value=0.1, max_value=500.0, value=16.0, step=0.1,
        help="Relative percent increase you want to detect (e.g. 16 for +16%)."
    )

with col2:
    st.subheader("Statistical Settings")
    alpha_percent = st.number_input("Significance level (α) %", min_value=0.1, max_value=20.0, value=5.0, step=0.1)
    power_percent = st.number_input("Power (1 - β) %", min_value=50.0, max_value=99.9, value=80.0, step=1.0)
    test_type = st.selectbox("Test type", ["Two-tailed (default)", "One-tailed"])

# convert to decimals
p1 = kpi_base / 100.0
mde_decimal = mde / 100.0
p2 = p1 * (1 + mde_decimal)
delta = abs(p2 - p1)

alpha = alpha_percent / 100.0
power = power_percent / 100.0

st.markdown("---")
st.subheader("Inputs / Expected")
c1, c2, c3 = st.columns(3)
c1.metric("Control rate (p1)", f"{p1:.4f}", f"{kpi_base:.2f}%")
c2.metric("Variant rate (p2)", f"{p2:.4f}", f"{p2*100:.2f}%")
c3.metric("Absolute lift (pp)", f"{(p2-p1)*100:.3f}pp", f"{mde:.3f}% relative")

# function using pooled formula
def pooled_sample_size(p1, p2, alpha, power, tails="two"):
    # choose z critical depending on tails
    if tails == "two":
        z_alpha = stats.norm.ppf(1 - alpha / 2.0)
    else:
        z_alpha = stats.norm.ppf(1 - alpha)  # one-tailed
    z_beta = stats.norm.ppf(power)
    pbar = (p1 + p2) / 2.0
    delta = abs(p2 - p1)
    # Optimizely / AB-testguide style pooled formula:
    # n_per_group = 2 * (z_alpha + z_beta)^2 * pbar * (1 - pbar) / delta^2
    n = 2.0 * (z_alpha + z_beta) ** 2 * pbar * (1 - pbar) / (delta ** 2)
    return int(np.ceil(n))

# compute both
n_two = pooled_sample_size(p1, p2, alpha, power, tails="two")
n_one = pooled_sample_size(p1, p2, alpha, power, tails="one")

st.markdown("---")
st.subheader("Required sample size (pooled formula)")

res_col1, res_col2 = st.columns(2)
res_col1.metric("Two-tailed (α/2)", f"{n_two:,}", help=f"Two-tailed α={alpha_percent}% power={power_percent}%")
res_col2.metric("One-tailed (α)", f"{n_one:,}", help=f"One-tailed α={alpha_percent}% power={power_percent}%")

# show the chosen option result
chosen = "two" if test_type.startswith("Two") else "one"
n_chosen = n_two if chosen == "two" else n_one
st.markdown("---")
st.subheader("Selected result")
st.write(f"Using **{test_type}** with α={alpha_percent}% and power={power_percent}% → **{n_chosen:,} per variant** ({n_chosen*2:,} total)")

# effect size (Cohen's h)
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
- Z_crit = Z_{1-α/2} (two-tailed) or Z_{1-α} (one-tailed)
- Z_β = Z_{power}

Examples with current inputs:
- Two-tailed → Z_crit = {stats.norm.ppf(1 - alpha/2):.6f}, Z_β = {stats.norm.ppf(power):.6f} → n = {n_two:,}
- One-tailed → Z_crit = {stats.norm.ppf(1 - alpha):.6f}, Z_β = {stats.norm.ppf(power):.6f} → n = {n_one:,}
""")

st.caption("Note: Many commercial calculators (including some Optimizely settings) use one-tailed tests by default — that is likely why your screenshot shows ≈3,800 per variation. Two-tailed tests are slightly more conservative and here give ≈4,804 for the same inputs.")
