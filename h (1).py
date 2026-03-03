import streamlit as st
import pandas as pd
import numpy_financial as npf
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="PIT Biogas Strategy Dashboard", layout="wide")
st.title("💡 Pragati Institute of Technology: Biogas Financial Dashboard")
st.markdown("Evaluating the feasibility of a 600 kg/day plant with ROI, NPV, and Inflation analysis.")

# --- SIDEBAR: INPUT VARIABLES ---
st.sidebar.header("Strategy Controls")

# Input: CSR Funding
csr_funding_lakhs = st.sidebar.slider("CSR Funding (in ₹ Lakhs)", 0, 100, 40)
csr_funding = csr_funding_lakhs * 100000

# Input: Economic Factors
inflation_rate = st.sidebar.slider("Expected Annual Inflation (%)", 0.0, 10.0, 5.0) / 100
discount_rate = st.sidebar.slider("Discount Rate (%)", 5.0, 15.0, 10.0) / 100

# --- DATA CONSTANTS (From Case Study) ---
TOTAL_CAPEX = 18000000 
BASE_LPG_SAVINGS = 2904000 
BASE_WASTE_SAVINGS = 330000 
GROSS_BASE_SAVINGS = BASE_LPG_SAVINGS + BASE_WASTE_SAVINGS 
BASE_MAINTENANCE = 600000 
EFFICIENCY = 0.90 
NET_CAPEX = TOTAL_CAPEX - csr_funding

# --- INFLATION-ADJUSTED CASH FLOW CALCULATIONS ---
cash_flows = [-NET_CAPEX]
annual_net_savings = []

for year in range(1, 11):
    inflated_gross = GROSS_BASE_SAVINGS * ((1 + inflation_rate) ** year)
    inflated_maint = BASE_MAINTENANCE * ((1 + inflation_rate) ** year)
    net_val = (inflated_gross * EFFICIENCY) - inflated_maint
    cash_flows.append(net_val)
    annual_net_savings.append(net_val)

# --- KEY METRICS ---
# 1. NPV Calculation (10 Years)
npv_value = npf.npv(discount_rate, cash_flows)

# 2. ROI Calculation (10 Years)
total_10yr_savings = sum(annual_net_savings)
total_10yr_profit = total_10yr_savings - NET_CAPEX
roi_pct = (total_10yr_profit / NET_CAPEX) * 100 if NET_CAPEX > 0 else 0

# 3. Payback Period
y1_savings = annual_net_savings[0]
payback = NET_CAPEX / y1_savings if y1_savings > 0 else 0

# 4. Fossil Fuel Reduction (8 cylinders replaced of 28 total)
lpg_reduction_pct = (8 / 28) * 100 

# --- DASHBOARD UI ---
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Net Investment", f"₹{NET_CAPEX/100000:.1f}L")
m2.metric("Payback", f"{payback:.2f} Yrs")
m3.metric("10-Year ROI", f"{roi_pct:.1f}%")
m4.metric("NPV", f"₹{npv_value/100000:.1f}L")
m5.metric("LPG Reduction", f"{lpg_reduction_pct:.1f}%")

st.divider()

# --- DECISION LOGIC ---
is_go = (payback < 8) and (npv_value > 0)

if is_go:
    st.success("### FINAL RECOMMENDATION: **GO** ✅")
else:
    st.error("### FINAL RECOMMENDATION: **NO-GO** ❌")

# --- VISUALIZATION ---
chart_col, data_col = st.columns([2, 1])

with chart_col:
    years = list(range(11))
    cumulative_cash = [sum(cash_flows[:i+1]) for i in range(11)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=cumulative_cash, mode='lines+markers', name='Cash Flow'))
    fig.add_hline(y=0, line_dash="dash", line_color="red")
    fig.update_layout(title="Cumulative Cash Flow (Inflation Adjusted)", xaxis_title="Years", yaxis_title="Rupees (₹)")
    st.plotly_chart(fig, use_container_width=True)

with data_col:
    st.subheader("Financial Detail")
    # Formatting strings carefully to avoid SyntaxErrors
    details = {
        "Metric": ["Net CAPEX", "10-Year Total Profit", "Total ROI (%)", "10-Year NPV", "Risk Buffer (10%)"],
        "Value": [
            f"₹{NET_CAPEX/100000:.1f}L",
            f"₹{total_10yr_profit/100000:.1f}L",
            f"{roi_pct:.2f}%",
            f"₹{npv_value/100000:.2f}L",
            f"₹{(y1_savings * 0.1)/100000:.2f}L"
        ]
    }
    st.table(pd.DataFrame(details))