# A/B Test Power Analysis Calculator

## Overview

A Streamlit application that calculates the required sample size for A/B tests using statistical power analysis. This tool helps marketing professionals determine the optimal audience size needed to detect meaningful differences between test variants.

## Purpose

Before running an A/B test, it's critical to ensure you collect enough data to make the results statistically valid. This calculator determines the minimum sample size required based on your current performance and the effect you want to detect.

## Requirements

- Python 3.7+
- streamlit
- statsmodels
- numpy

## Installation

```bash
pip install streamlit statsmodels numpy
```

## Usage

Run the application:

```bash
streamlit run script.py
```

## Input Parameters

**Variable Inputs:**
- **Current KPI (Conversion Rate):** Your baseline conversion rate as a percentage (e.g., 12 for 12%)
  - Recommendation: Use daily average over the past 3-6 months
- **Minimum Detectable Effect (MDE):** The relative percentage increase you want to detect (e.g., 16 for 16% improvement)
  - Small changes (CTA, colors): 5-15%
  - Major changes (redesign, new logo): 20-30%

**Fixed Parameters:**
- Statistical Power: 80% (0.8)
- Significance Level: 5% (0.05)
- Test Type: Two-tailed

## Output

The calculator provides:
- Required sample size per variant (Control and Variant)
- Total sample size needed
- Effect size (Cohen's h)
- Expected conversion rates for both groups
- Absolute and relative lift calculations

## Methodology

The calculation uses a two-proportion z-test to determine sample size:

1. Converts input percentages to decimal proportions
2. Calculates expected variant rate: Base + (Base × MDE)
3. Computes effect size using Cohen's h
4. Determines sample size using statsmodels' `zt_ind_solve_power` function

## Example

**Input:**
- Current KPI: 12%
- MDE: 16%

**Calculation:**
- Control rate: 0.12 (12%)
- Expected variant rate: 0.12 + (0.12 × 0.16) = 0.14 (14%)
- Output: Sample size required per variant

## References

Based on standard statistical power analysis methods for proportion tests. Implementation uses statsmodels library for accurate statistical calculations.

## Notes

- Sample sizes are rounded up to ensure adequate power
- The tool assumes equal sample sizes for both variants (1:1 ratio)
- Results provide 80% probability of detecting the specified effect if it truly exists
- 95% confidence level means 5% chance of false positive results
