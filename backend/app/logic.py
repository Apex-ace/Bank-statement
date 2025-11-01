import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from .models import StatementData

# --- PydanticAI Setup with Gemini (via GoogleModel) ---
# Ensure you have GOOGLE_API_KEY in your environment
google_provider = GoogleProvider(api_key=os.getenv("GOOGLE_API_KEY"))
llm = GoogleModel("gemini-2.5-flash", provider=google_provider)
agent = Agent(model=llm)


def process_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF.
    Handles both text-based and scanned (image-based) PDFs.
    """
    full_text = ""
    
    # 1. Try direct text extraction with PyMuPDF
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                full_text += page.get_text()
    except Exception as e:
        print(f"PyMuPDF error: {e}. Defaulting to OCR.")
        full_text = ""  # Force OCR fallback

    # 2. If text is minimal, it’s likely scanned → use OCR
    if len(full_text.strip()) < 100:
        print("Minimal text extracted. Attempting OCR...")
        try:
            images = convert_from_bytes(file_bytes)
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)
            full_text = ocr_text
            print("OCR extraction successful.")
        except Exception as ocr_error:
            print(f"OCR processing failed: {ocr_error}")
            if not full_text:
                raise ValueError("Both text extraction and OCR failed.")
    
    return full_text


async def extract_transactions(statement_text: str) -> StatementData:
    """
    Uses PydanticAI to extract structured transaction data from raw text.
    """
    if not statement_text.strip():
        raise ValueError("The provided PDF is empty or could not be read.")

    print("Sending text to PydanticAI agent...")

    prompt = f"""
    You are an expert financial analyst. Please extract all individual transactions
    from the following bank statement text. Ignore summary sections, marketing
    text, and disclaimers. Focus only on the itemized list of transactions.
    
    Statement Text:
    ---
    {statement_text[:10000]}
    ---
    
    Extract all transactions into the provided JSON schema.
    """

    try:
        result = await agent.run(  # <-- Added 'await'
            prompt,
            output_type=StatementData  # <-- Changed to 'output_type'
        )
        print("PydanticAI extraction successful.")
        return result.output  # .output contains validated Pydantic model
    except Exception as e:
        print(f"PydanticAI extraction failed: {e}")
        raise RuntimeError(f"Failed to parse statement: {e}")
