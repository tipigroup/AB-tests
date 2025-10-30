import streamlit as st
import numpy as np
from statsmodels.stats.proportion import proportion_effectsize
from statsmodels.stats.power import zt_ind_solve_power

# Page configuration
st.set_page_config(page_title="A/B Test Power Analysis", layout="wide")

# Title and introduction
st.title("A/B Test Power Analysis Calculator")
st.markdown("""
This tool helps you determine the optimal sample size for your A/B tests. 
Input your current KPI performance and the minimum effect you want to detect, 
and this tool will calculate the required audience size for each variant.
""")

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Parameters")
    
    # KPI Base input
    kpi_base = st.number_input(
        "Current KPI (Conversion Rate)",
        min_value=0.01,
        max_value=100.0,
        value=12.0,
        step=0.1,
        help="Enter your current conversion rate as a percentage (e.g., 12 for 12%)"
    )
    
    # Convert to decimal
    kpi_base_decimal = kpi_base / 100
    
    # MDE input
    mde = st.number_input(
        "Minimum Detectable Effect (MDE) %",
        min_value=1.0,
        max_value=100.0,
        value=16.0,
        step=0.5,
        help="The percentage increase you want to be able to detect (e.g., 16 for a 16% relative increase)"
    )
    
    # Convert to decimal
    mde_decimal = mde / 100

with col2:
    st.subheader("Fixed Parameters")
    st.metric("Statistical Power", "80%", help="Probability of detecting an effect when it exists")
    st.metric("Significance Level (α)", "5%", help="Probability of false positive (Type I error)")
    st.metric("Test Type", "Two-tailed", help="Tests for differences in both directions")

# Calculate the expected KPI after the effect
kpi_variant = kpi_base_decimal + (kpi_base_decimal * mde_decimal)

# Display the calculation
st.markdown("---")
st.subheader("Expected Results")

col3, col4, col5 = st.columns(3)

with col3:
    st.metric("Control Group Rate", f"{kpi_base_decimal:.4f}", f"{kpi_base:.2f}%")

with col4:
    st.metric("Expected Variant Rate", f"{kpi_variant:.4f}", f"{kpi_variant*100:.2f}%")

with col5:
    absolute_lift = (kpi_variant - kpi_base_decimal) * 100
    st.metric("Absolute Lift", f"{absolute_lift:.2f}pp", f"+{mde:.1f}% relative")

# Calculate effect size
effect_size = proportion_effectsize(kpi_base_decimal, kpi_variant)

# Calculate sample size per group
try:
    sample_size_per_group = zt_ind_solve_power(
        effect_size=effect_size,
        alpha=0.05,  # Significance level
        power=0.8,   # Statistical power
        ratio=1.0,   # Equal sample sizes
        alternative='two-sided'
    )
    
    # Round up to nearest integer
    sample_size_per_group = int(np.ceil(sample_size_per_group))
    total_sample_size = sample_size_per_group * 2
    
    # Display results
    st.markdown("---")
    st.subheader("Required Sample Size")
    
    result_col1, result_col2, result_col3 = st.columns(3)
    
    with result_col1:
        st.metric("Per Variant", f"{sample_size_per_group:,}", help="Sample size needed for each group (Control and Variant)")
    
    with result_col2:
        st.metric("Total Sample Size", f"{total_sample_size:,}", help="Combined sample size for both groups")
    
    with result_col3:
        st.metric("Effect Size (Cohen's h)", f"{effect_size:.4f}", help="Standardized measure of the difference")
    
    # Additional information
    st.markdown("---")
    st.subheader("Test Summary")
    
    st.info(f"""
    **Test Configuration:**
    - **Control Group:** {sample_size_per_group:,} visitors at {kpi_base:.2f}% conversion rate
    - **Variant Group:** {sample_size_per_group:,} visitors at expected {kpi_variant*100:.2f}% conversion rate
    - **Total Audience Required:** {total_sample_size:,} visitors
    - **Confidence Level:** 95% (α = 0.05)
    - **Statistical Power:** 80% (β = 0.20)
    
    With this sample size, there is an 80% chance of detecting a {mde:.1f}% relative increase 
    (from {kpi_base:.2f}% to {kpi_variant*100:.2f}%) if it truly exists, with 95% confidence.
    """)
    
    # Calculation notes
    with st.expander("Calculation Logic"):
        st.markdown(f"""
        **Step-by-step calculation:**
        
        1. **Base KPI (p₁):** {kpi_base_decimal:.4f} ({kpi_base:.2f}%)
        
        2. **Minimum Detectable Effect:** {mde:.1f}%
        
        3. **Expected Variant KPI (p₂):** 
           - Formula: p₂ = p₁ + (p₁ × MDE)
           - Calculation: {kpi_base_decimal:.4f} + ({kpi_base_decimal:.4f} × {mde_decimal:.4f}) = {kpi_variant:.4f}
        
        4. **Effect Size (Cohen's h):** {effect_size:.4f}
           - This standardizes the difference between proportions
        
        5. **Sample Size Calculation:**
           - Using the effect size, power (0.8), and significance level (0.05)
           - Statistical test: Two-proportion z-test (two-tailed)
           - Result: {sample_size_per_group:,} per group, {total_sample_size:,} total
        """)

except Exception as e:
    st.error(f"Error calculating sample size: {str(e)}")
    st.info("Please check your input parameters and try again.")

# Footer
st.markdown("---")
st.caption("For more accurate results, use the daily average KPI from the past 3-6 months. Consider the magnitude of each change when estimating MDE (small CTA changes might need 5-15%, major redesigns could use 20-30%).")