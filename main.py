from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from typing import List
from enum import Enum
from uuid import uuid4
from datetime import date


app = FastAPI()

# Define allowed account types
class AccountType(str, Enum):
    business = "business"
    personal = "personal"

# Schema for creating an account
class AccountCreate(BaseModel):
    type: AccountType
    person_name: str
    address: str

# Schema for full account (with ID)
class Account(AccountCreate):
    id: int

from pydantic import BaseModel

class PaymentCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount_in_euros: int
    payment_date: date

class Payment(PaymentCreate):
    id: str


# In-memory list to simulate database
accounts: List[Account] = []
next_id = 1
payments: List[Payment] = []

@app.post("/accounts/", response_model=Account)
def create_account(account: AccountCreate):
    global next_id
    new_account = Account(id=next_id, **account.dict())
    accounts.append(new_account)
    next_id += 1
    return new_account

@app.get("/accounts/", response_model=List[Account])
def get_all_accounts():
    return accounts

@app.get("/accounts/{account_id}", response_model=Account)
def get_account_by_id(account_id: int):
    for acc in accounts:
        if acc.id == account_id:
            return acc
    raise HTTPException(status_code=404, detail="Account not found")

@app.delete("/accounts/{account_id}")
def delete_account(account_id: int):
    for i, acc in enumerate(accounts):
        if acc.id == account_id:
            del accounts[i]
            return {"detail": "Account deleted"}
    raise HTTPException(status_code=404, detail="Account not found")

@app.post("/payments/", response_model=Payment)
def create_payment(payment: PaymentCreate):
    # Validation: Amount must be > 0
    if payment.amount_in_euros <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # Validation: from and to accounts must exist
    from_exists = any(acc.id == payment.from_account_id for acc in accounts)
    to_exists = any(acc.id == payment.to_account_id for acc in accounts)

    if not (from_exists and to_exists):
        raise HTTPException(status_code=400, detail="Invalid account ID(s)")

    new_payment = Payment(id=str(uuid4()), **payment.dict())
    payments.append(new_payment)
    return new_payment

@app.get("/payments/", response_model=List[Payment])
def get_all_payments():
    return payments

@app.get("/payments/{payment_id}", response_model=Payment)
def get_payment_by_id(payment_id: str):
    for payment in payments:
        if payment.id == payment_id:
            return payment
    raise HTTPException(status_code=404, detail="Payment not found")

