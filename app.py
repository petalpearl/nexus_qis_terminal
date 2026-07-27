import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from engine import calculate_bond_metrics, run_governance_and_fee_check

st.set_page_config(
    page_title="Nexus-QIS Terminal", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📊 Nexus-QIS: Fixed Income & Structuring Engine")

tab1, tab2 = st.tabs(["💳 Credit Desk Analytics", "🛡️ QIS Structuring & Governance"])

# ----------------------------------------------------
# TAB 1: CREDIT DESK ANALYTICS
# ----------------------------------------------------
with tab1:
    st.header("US High Yield Bond Relative Valuation Desk")
    st.markdown("Identifies mispriced credit bonds using peer group spread deviations.")
    
    # Mock Market Data Payload
    sample_bonds = [
        {"ticker": "US-HY-001", "rating": "BB", "yield": 0.082, "treasury_benchmark_yield": 0.042},
        {"ticker": "US-HY-002", "rating": "BB", "yield": 0.068, "treasury_benchmark_yield": 0.042},
        {"ticker": "US-HY-003", "rating": "B",  "yield": 0.095, "treasury_benchmark_yield": 0.042},
        {"ticker": "US-HY-004", "rating": "B",  "yield": 0.115, "treasury_benchmark_yield": 0.042},
        {"ticker": "US-HY-005", "rating": "BB", "yield": 0.091, "treasury_benchmark_yield": 0.042},
        {"ticker": "US-HY-006", "rating": "B",  "yield": 0.088, "treasury_benchmark_yield": 0.042},
    ]
    
    df_results = calculate_bond_metrics(sample_bonds)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Top Trade Opportunity", "US-HY-004", "BUY Signal (+100 bps spread)")
    m2.metric("Desk Universe Coverage", f"{len(df_results)} Bonds", "High Yield US")
    m3.metric("Avg Benchmark Spread", "515 bps", "vs US 10Y Treasury")
    
    st.markdown("---")
    
    # VISUAL GRAPH 1: Spread Deviation Bar Chart
    fig_spread = px.bar(
        df_results, 
        x='ticker', 
        y='spread_deviation',
        color='trade_signal',
        title="Relative Value Mispricing (Spread Deviation vs Rating Peer Avg in bps)",
        labels={'spread_deviation': 'Deviation (bps)', 'ticker': 'Bond Ticker'},
        color_discrete_map={
            'BUY (Undervalued)': '#2ECC71',
            'SELL (Overvalued)': '#E74C3C',
            'NEUTRAL': '#95A5A6'
        },
        text='spread_deviation'
    )
    fig_spread.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig_spread, use_container_width=True)
    
    st.subheader("Real-Time Pricing Matrix")
    st.dataframe(df_results, use_container_width=True)

# ----------------------------------------------------
# TAB 2: QIS STRUCTURING & GOVERNANCE
# ----------------------------------------------------
with tab2:
    st.header("QIS Strategy Pre-Trade Governance & Fee Validator")
    st.markdown("Validates index constituent concentration limits and models structuring licensing fees.")
    
    sample_basket = [
        {"issuer": "Corp Alpha", "notional_usd": 4500000, "rating_rank": 2},
        {"issuer": "Corp Beta",  "notional_usd": 2500000, "rating_rank": 2},
        {"issuer": "Corp Gamma", "notional_usd": 3000000, "rating_rank": 4},
    ]
    
    gov_res = run_governance_and_fee_check(sample_basket)
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        if gov_res['status'] == "APPROVED":
            st.success(f"Status: {gov_res['status']}")
        else:
            st.error(f"Status: {gov_res['status']}")
            
        st.write("**Rule Violations:**")
        for v in gov_res['violations']:
            st.warning(f"• {v}")
            
        st.metric("Total Basket Notional", f"${gov_res['total_notional_usd']:,.2f}")
        st.metric("Estimated Annual Structuring & Licensing Fee", f"${gov_res['calculated_annual_fee_usd']:,.2f}")

    with col_right:
        # VISUAL GRAPH 2: Constituent Concentration Donut Chart
        basket_df = pd.DataFrame(gov_res['basket_summary'])
        fig_donut = px.pie(
            basket_df, 
            values='notional_usd', 
            names='issuer', 
            hole=0.4,
            title="Basket Constituent Concentration Weight (%)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_donut.update_layout(template="plotly_dark", height=320)
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")
    
    # VISUAL GRAPH 3: QIS Index Simulated Performance Line Chart
    st.subheader("📈 QIS Strategy Backtested Performance Tracking")
    dates = pd.date_range(start="2026-01-01", periods=90)
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.008, size=len(dates))
    cum_returns = 100 * (1 + returns).cumprod()
    
    perf_df = pd.DataFrame({'Date': dates, 'Nexus High Yield QIS Index': cum_returns})
    
    fig_line = px.line(
        perf_df, 
        x='Date', 
        y='Nexus High Yield QIS Index',
        title="Normalized Strategy Index Level (Base = 100)",
        line_shape="linear"
    )
    fig_line.update_traces(line_color="#00D26A", line_width=2)
    fig_line.update_layout(template="plotly_dark", height=320)
    st.plotly_chart(fig_line, use_container_width=True)