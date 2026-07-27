import pandas as pd
import numpy as np

# 1. Credit Trading: Relative Valuation & Spread Analytics
def calculate_bond_metrics(bonds_data):
    df = pd.DataFrame(bonds_data)
    # Calculate Credit Spread over US Treasury Benchmark (bps)
    df['credit_spread_bps'] = (df['yield'] - df['treasury_benchmark_yield']) * 10000
    
    # Calculate Rating Peer Group Average Spread
    rating_averages = df.groupby('rating')['credit_spread_bps'].transform('mean')
    df['peer_avg_spread'] = rating_averages
    
    # Flag Trade Ideas: If spread is > 75 bps wider than peer avg, it's undervalued (BUY signal)
    df['spread_deviation'] = df['credit_spread_bps'] - df['peer_avg_spread']
    df['trade_signal'] = np.where(df['spread_deviation'] > 75, 'BUY (Undervalued)', 
                        np.where(df['spread_deviation'] < -75, 'SELL (Overvalued)', 'NEUTRAL'))
    return df

# 2. QIS Structuring: Fee Engine & Governance Checker
def run_governance_and_fee_check(basket_data, max_weight=0.30, min_rating_rank=2):
    """
    Rating Rank: 1=AAA, 2=BBB, 3=BB (High Yield), 4=CCC
    """
    df = pd.DataFrame(basket_data)
    total_notional = df['notional_usd'].sum()
    df['weight'] = df['notional_usd'] / total_notional
    
    violations = []
    
    # Rule 1: Single Issuer Concentration Check
    overweighted = df[df['weight'] > max_weight]
    if not overweighted.empty:
        for _, row in overweighted.iterrows():
            violations.append(f"Concentration Risk: {row['issuer']} weight ({row['weight']:.1%}) exceeds max limit ({max_weight:.1%})")
            
    # Rule 2: Rating Eligibility
    disqualified = df[df['rating_rank'] > min_rating_rank]
    if not disqualified.empty:
        for _, row in disqualified.iterrows():
            violations.append(f"Credit Quality Violation: {row['issuer']} rating exceeds risk limit threshold.")
            
    # QIS Fee Calculation (Management Fee + Licensing Fee)
    mgmt_fee_bps = 50  # 0.50%
    licensing_fee_bps = 15  # 0.15%
    total_fee_usd = total_notional * ((mgmt_fee_bps + licensing_fee_bps) / 10000)
    
    status = "APPROVED" if len(violations) == 0 else "REJECTED"
    
    return {
        "status": status,
        "violations": violations,
        "total_notional_usd": total_notional,
        "calculated_annual_fee_usd": total_fee_usd,
        "basket_summary": df[['issuer', 'weight', 'notional_usd']].to_dict(orient='records')
    }