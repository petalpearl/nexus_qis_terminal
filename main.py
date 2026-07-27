from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from engine import calculate_bond_metrics, run_governance_and_fee_check

app = FastAPI(title="Nexus-QIS API", version="1.0")

class BondItem(BaseModel):
    ticker: str
    rating: str
    yield_val: float  # Renamed yield to yield_val for Python keyword safety
    treasury_benchmark_yield: float

class BasketItem(BaseModel):
    issuer: str
    notional_usd: float
    rating_rank: int

@app.get("/")
def root():
    return {"status": "Nexus-QIS Trading & Structuring Engine Online"}

@app.post("/v1/credit/relative-value")
def credit_analytics(bonds: List[BondItem]):
    data = [{
        'ticker': b.ticker, 
        'rating': b.rating, 
        'yield': b.yield_val, 
        'treasury_benchmark_yield': b.treasury_benchmark_yield
    } for b in bonds]
    
    res_df = calculate_bond_metrics(data)
    return res_df.to_dict(orient="records")

@app.post("/v1/qis/governance-check")
def governance_check(basket: List[BasketItem]):
    data = [b.dict() for b in basket]
    result = run_governance_and_fee_check(data)
    return result