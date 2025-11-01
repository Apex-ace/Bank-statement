from dotenv import load_dotenv
load_dotenv() 

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from .logic import process_pdf, extract_transactions
from .models import StatementData

app = FastAPI(
    title="Statement Extractor AI",
    description="Upload bank statements (PDF) and get structured JSON data back, powered by PydanticAI."
)

# --- THIS IS THE FINAL FIX ---
# We must specify the exact URLs that are allowed to make requests.
origins = [
    "https://statement-extractor-frontend.onrender.com", # Your live frontend
    "http://localhost:3000", # For local testing
    "http://127.0.0.1:3000"   # For local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End of FIX ---

@app.get("/")
def read_root():
    return {"message": "PydanticAI Statement Extractor is running. POST to /upload"}

@app.post("/upload", response_model=StatementData)
async def upload_statement(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        file_bytes = await file.read()
        raw_text = process_pdf(file_bytes)
        structured_data = await extract_transactions(raw_text)
        
        if not structured_data or not structured_data.transactions:
             raise HTTPException(status_code=404, detail="No transactions could be found in the document.")

        return structured_data

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        print(f"An unexpected error occurred: {e}") 
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred.")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

