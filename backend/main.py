from fastapi import FastAPI
from pydantic import BaseModel
from finance import calculate_repayment

app = FastAPI()

class LoanRequest(BaseModel):
    salary: float
    loan_amount: float
    interest_rate: float
    months: int
    frequency: str  # "monthly" or "weekly"

@app.get("/health")
def health():
    return {"status": "running"}

@app.post("/calculate_advance")
def calculate_advance(data: LoanRequest):
    return calculate_repayment(data)
