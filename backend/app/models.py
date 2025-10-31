from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Transaction(BaseModel):
    """
    A single transaction from a bank statement.
    """
    date: str = Field(..., description="The date of the transaction (e.g., YYYY-MM-DD or MM/DD/YYYY)")
    description: str = Field(..., description="The merchant or transaction description")
    amount: float = Field(..., description="The numerical amount of the transaction")
    transaction_type: Literal["Debit", "Credit"] = Field(..., description="Whether the transaction is a Debit (money out) or Credit (money in)")
    balance: Optional[float] = Field(None, description="The running balance after the transaction, if available")

class StatementData(BaseModel):
    """
    A comprehensive model to hold all extracted transactions
    from a bank statement.
    """
    account_holder: Optional[str] = Field(None, description="The name of the account holder")
    statement_period: Optional[str] = Field(None, description="The period the statement covers (e.g., 'Oct 1 - Oct 31, 2025')")
    transactions: List[Transaction] = Field(..., description="A list of all transactions found in the statement")