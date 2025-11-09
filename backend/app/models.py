from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Transaction(BaseModel):
    date: str = Field(..., description="The date of the transaction")
    description: str = Field(..., description="The merchant or transaction description")
    amount: float = Field(..., description="The numerical amount of the transaction")
    transaction_type: Literal["Debit", "Credit"] = Field(..., description="Whether the transaction is a Debit or Credit")
    balance: Optional[float] = Field(None, description="The running balance after the transaction, if available")

class StatementData(BaseModel):
    account_holder: Optional[str] = Field(None, description="The name of the account holder")
    statement_period: Optional[str] = Field(None, description="The period the statement covers")
    transactions: List[Transaction] = Field(..., description="A list of all *clean* transactions")

class RawTransaction(BaseModel):
    date: Optional[str] = Field(None, description="The date of the entry, if present")
    description: Optional[str] = Field(None, description="The description of the entry")
    debit: Optional[str] = Field(None, description="The debit amount as a string, if present")
    credit: Optional[str] = Field(None, description="The credit amount as a string, if present")
    balance: Optional[str] = Field(None, description="The balance as a string, if present")

class RawStatementData(BaseModel):
    transactions: List[RawTransaction]
    account_holder: Optional[str] = Field(None, description="The account holder's name")
    statement_period: Optional[str] = Field(None, description="The statement period")