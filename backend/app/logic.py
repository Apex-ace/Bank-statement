import os
import fitz
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import asyncio
import io
import platform # Import platform to check OS

# (All Windows paths have been removed)

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
try:
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# FIX: Import from 'models' (no dot)
from models import RawStatementData

openai_agent = None
google_agent = None

if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
    openai_provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    openai_llm = OpenAIModel("gpt-5", provider=openai_provider)
    openai_agent = Agent(model=openai_llm)

if os.getenv("GOOGLE_API_KEY"):
    google_provider = GoogleProvider(api_key=os.getenv("GOOGLE_API_KEY"))
    google_llm = GoogleModel("gemini-2.5-flash", provider=google_provider)
    google_agent = Agent(model=google_llm)


def get_text_from_pdf(file_bytes: bytes) -> str:
    full_text = ""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                full_text += page.get_text()
    except Exception:
        full_text = ""

    if len(full_text.strip()) < 100:
        try:
            # This is the simple, cross-platform version
            images = convert_from_bytes(file_bytes)
                
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)
            full_text = ocr_text
        except Exception as e:
            print(f"pdf2image OCR failed: {e}")
            full_text = ""
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

    prompt = f"""
You are an expert data entry clerk. Extract all individual transaction lines
from the following bank statement text. Pay close attention to the 'Debits' and 'Credits' columns.
If a date is on one line, it applies to the lines below it until a new date appears.
Extract 'account_holder' and 'statement_period' if you find them.
Ignore summary lines like 'Balance brought forward'.

Statement Text:
---
{statement_text[:10000]}
---

Extract all transaction lines you see into the provided JSON schema.
"""

    last_exc = None

    if openai_agent:
        try:
            return await _run_with_agent(openai_agent, prompt)
        except Exception as e:
            last_exc = e
            msg = str(e).lower()
            if not ("insufficient_quota" in msg or "quota" in msg or "429" in msg or "rate limit" in msg):
                raise RuntimeError(f"OpenAI error: {e}") from e

    if google_agent:
        try:
            return await _run_with_agent(google_agent, prompt)
        except Exception as e:
            raise RuntimeError(f"Both primary and fallback LLMs failed. Last error: {e}") from e

    if last_exc:
        raise RuntimeError(f"No available LLM succeeded. Primary error: {last_exc}")
    raise RuntimeError("No LLM is configured. Set OPENAI_API_KEY and/or GOOGLE_API_KEY in env.")