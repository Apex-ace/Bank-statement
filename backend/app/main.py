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

origins = [
    "https://statement-extractor-frontend.onrender.com", 
    "http://localhost:3000", 
    "http://127.0.0.1:3000"   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # <-- Use the specific list here
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
    """
    The main endpoint.
    1. Accepts a PDF file.
    2. Processes it (OCR or text extraction).
    3. Uses PydanticAI to extract transactions.
    4. Returns the structured JSON data.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        file_bytes = await file.read()
        
        # 1. Process PDF (text or OCR)
        # process_pdf is synchronous, so no await
        raw_text = process_pdf(file_bytes)
        
        # 2. Extract with PydanticAI
        structured_data = await extract_transactions(raw_text) # This is correct
        
        if not structured_data or not structured_data.transactions:
             raise HTTPException(status_code=404, detail="No transactions could be found in the document.")

        # 3. Return JSON
        return structured_data

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        # Log the full exception for debugging
        print(f"An unexpected error occurred: {e}") 
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred.")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
