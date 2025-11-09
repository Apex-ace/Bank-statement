from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import List

# FIX: Import from 'logic' and 'models' (no dots)
from logic import get_text_from_pdf, get_text_from_image, extract_raw_transactions
from models import StatementData, Transaction, RawStatementData, RawTransaction

app = FastAPI(
    title="Statement Extractor AI",
    description="Upload bank statements (PDF or Image) and get structured JSON data back, powered by PydanticAI."
)


origins = [
    "https://bank-statement-frontend-k3xn.onrender.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_value(value: str) -> float:
    if value is None:
        return None
    try:
        return float(value.replace(',', '').replace(':', '.'))
    except (ValueError, TypeError):
        return None

def process_raw_data(raw_data: RawStatementData) -> StatementData:
    final_transactions: List[Transaction] = []
    current_date = None

    for raw_tx in raw_data.transactions:
        if raw_tx.date:
            current_date = raw_tx.date

        debit_val = clean_value(raw_tx.debit)
        credit_val = clean_value(raw_tx.credit)
        balance_val = clean_value(raw_tx.balance)

        if debit_val is None and credit_val is None:
            continue
        
        if debit_val:
            tx_type = "Debit"
            amount = debit_val
        else:
            tx_type = "Credit"
            amount = credit_val

        final_transactions.append(
            Transaction(
                date=current_date or "N/A",
                description=(raw_tx.description or "N/A").strip(),
                amount=amount,
                transaction_type=tx_type,
                balance=balance_val
            )
        )

    return StatementData(
        account_holder=raw_data.account_holder,
        statement_period=raw_data.statement_period,
        transactions=final_transactions
    )


@app.get("/")
def read_root():
    return {"message": "PydanticAI Statement Extractor is running. POST to /upload"}

@app.post("/upload", response_model=StatementData)
async def upload_statement(file: UploadFile = File(...)):
    
    if not (file.content_type == "application/pdf" or file.content_type.startswith("image/")):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF or an image (PNG, JPG).")

    try:
        file_bytes = await file.read()
        raw_text = ""

        if file.content_type == "application/pdf":
            raw_text = get_text_from_pdf(file_bytes)
        elif file.content_type.startswith("image/"):
            raw_text = get_text_from_image(file_bytes)

        raw_data = await extract_raw_transactions(raw_text)
        structured_data = process_raw_data(raw_data)

        if not structured_data or not structured_data.transactions:
            raise HTTPException(status_code=404, detail="No transactions could be found in the document.")

        return structured_data

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

# This part is only for local development
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)