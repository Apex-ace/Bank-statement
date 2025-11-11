import os
import fitz 
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import asyncio
import io
import platform 

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
try:
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

from models import RawStatementData

openai_agent = None
google_agent = None

if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
    openai_provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    openai_llm = OpenAIModel("gpt-4o-mini", provider=openai_provider) 
    openai_agent = Agent(model=openai_llm)

if os.getenv("GOOGLE_API_KEY"):
    google_provider = GoogleProvider(api_key=os.getenv("GOOGLE_API_KEY"))
    google_llm = GoogleModel("gemini-2.5-flash", provider=google_provider)
    google_agent = Agent(model=google_llm)


def get_text_from_pdf(file_bytes: bytes) -> str:
    full_text = ""
    page_count = 0
    try:
        # 1. First, try fast text extraction and get page count
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            page_count = doc.page_count
            for page in doc:
                full_text += page.get_text()
    except Exception as e:
        print(f"Fitz (PyMuPDF) failed: {e}")
        # If fitz fails, we can't get page count this way
        full_text = ""
        page_count = 0 # Reset

    # 2. If fast extraction fails (e.g., scanned PDF), use slow, memory-efficient OCR
    if len(full_text.strip()) < 100:
        print("Fast text extraction failed, falling back to OCR...")
        ocr_text = ""
        
        # If fitz failed to get a page_count, we can't loop.
        # As a last resort, try to convert just the first page.
        # This avoids the memory crash but might miss data on other pages.
        if page_count == 0:
            print("Warning: Could not get page count. Only processing first page to avoid memory crash.")
            page_count = 1 # Process just one page

        try:
            # Loop and process ONE page at a time to save RAM
            for i in range(1, page_count + 1):
                print(f"OCR processing page {i}/{page_count}...")
                
                # Convert only the single, current page
                images = convert_from_bytes(
                    file_bytes,
                    first_page=i,
                    last_page=i,
                    fmt='png',
                    thread_count=1 
                )
                
                if images:
                    ocr_text += pytesseract.image_to_string(images[0])
                    images[0].close()

            full_text = ocr_text
            print("OCR processing complete.")
        except Exception as e:
            print(f"pdf2image OCR failed: {e}")
            # Return whatever fitz got, even if it was empty
            return full_text
            
    return full_text


def get_text_from_image(file_bytes: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(file_bytes))
        ocr_text = pytesseract.image_to_string(img)
        return ocr_text
    except Exception as e:
        print(f"Image OCR failed: {e}")
        return ""


async def _run_with_agent(agent: Agent, prompt: str) -> RawStatementData:
    result = await agent.run(prompt, output_type=RawStatementData)
    return result.output


async def extract_raw_transactions(statement_text: str) -> RawStatementData:
    if not statement_text.strip():
        raise ValueError("The provided document is empty or could not be read.")

    truncated_text = statement_text[:12000]

    prompt = f"""
You are an expert data entry clerk. Extract all individual transaction lines
from the following bank statements text. Pay close attention to the 'Debits' and 'Credits' columns.
If a date is on one line, it applies to the lines below it until a new date appears.
Extract 'account_holder' and 'statement_period' if you find them.
Ignore summary lines like 'Balance brought forward'.

Statement Text:
---
{truncated_text}
---

Extract all transaction lines you see into the provided JSON schema.
"""

    last_exc = None

    # Try Google Gemini first
    if google_agent:
        try:
            return await _run_with_agent(google_agent, prompt)
        except Exception as e:
            last_exc = e
            print(f"Google Gemini failed: {e}")

    # Fallback to OpenAI
    if openai_agent:
        try:
            print("Falling back to OpenAI...")
            return await _run_with_agent(openai_agent, prompt)
        except Exception as e:
            print(f"OpenAI failed: {e}")
            last_exc = e
            msg = str(e).lower()
            if not ("insufficient_quota" in msg or "quota" in msg or "429" in msg or "rate limit" in msg):
                raise RuntimeError(f"OpenAI error: {e}") from e

    if last_exc:
        raise RuntimeError(f"Both primary and fallback LLMs failed. Last error: {last_exc}")
    raise RuntimeError("No LLM is configured. Set OPENAI_API_KEY and/or GOOGLE_API_KEY in env.")