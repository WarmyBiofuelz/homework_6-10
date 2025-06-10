from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from typing import List
from enum import Enum

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

# In-memory list to simulate database
accounts: List[Account] = []
next_id = 1

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
