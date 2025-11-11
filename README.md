# Statement Extractor AI

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-blue?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PydanticAI](https://img.shields.io/badge/PydanticAI-blue?logo=pydantic)](https://github.com/pydantic/pydantic-ai)

A full-stack AI-powered web application designed to extract and structure transaction data from bank statements. Upload a PDF or use your camera (including a live-scanning mode), and the system uses AI (Gemini/OpenAI) to parse the text and return a clean, tabular list of transactions.

**Live Frontend Demo:** [https://bank-statement-frontend-k3xn.onrender.com](https://bank-statement-frontend-k3xn.onrender.com)

##  Key Features

### Frontend (Client)
* **Drag & Drop Upload:** Modern dropzone for PDF and image files (`.pdf`, `.jpg`, `.png`).
* **Live Camera Scanning:** Access your device's camera to scan physical documents.
* **Real-time "Live Upload":** A special mode that captures a frame from the camera every 2.5 seconds and automatically uploads it for extraction, allowing for continuous scanning.
* **Dynamic Data Grid:** Displays all extracted transactions (from multiple uploads) in a searchable, sortable AG Grid.
* **Data Summary:** Calculates and displays total credit and debit amounts.
* **CSV Export:** Export all transactions in the grid to a CSV file.
* **Real-time Progress:** Shows a detailed progress bar for upload and server processing.

### Backend (Server)
* **FastAPI Backend:** A high-performance Python server.
* **AI-Powered Extraction:** Uses `PydanticAI` to intelligently extract text and parse it into a structured `StatementData` model.
* **LLM Fallback Logic:**
    1.  Tries **OpenAI** (e.g., `gpt-5`) first.
    2.  If OpenAI fails (e.g., quota error), it automatically falls back to **Google Gemini** (e.g., `gemini-2.5-flash`).
* **Hybrid PDF Processing:**
    1.  First, attempts fast text extraction using `PyMuPDF` (fitz).
    2.  If the extracted text is poor (e.g., a scanned PDF), it automatically falls back to robust OCR using `pdf2image` and `pytesseract`.
* **Image OCR:** Full support for image uploads (`.png`, `.jpg`) using `pytesseract`.
* **Data Cleaning:** Post-processes the "raw" AI output to clean data, convert types, and ensure a consistent `Transaction` list.

##  Architecture

The application is a decoupled full-stack project:

1.  **Frontend:** A static website (Vanilla HTML, CSS, JavaScript) that runs entirely in the browser. It sends files to the backend via an XHR (AJAX) request.
2.  **Backend:** A Python FastAPI server that exposes a single `/upload` endpoint.
    * The `/upload` endpoint accepts a `multipart/form-data` file.
    * It uses `logic.py` to get raw text (via PyMuPDF, Pytesseract, or pdf2image).
    * It passes the raw text to a PydanticAI `Agent` (configured with Gemini/OpenAI).
    * The agent returns structured `RawStatementData` (defined in `models.py`).
    * `main.py` cleans this raw data into the final `StatementData` model.
    * The final JSON is sent back to the frontend.
3.  **Frontend (Again):** The JavaScript (`app.js`) receives the JSON, appends the new transactions to the AG Grid, and updates the summary.

##  Tech Stack

* **Backend:**
    * **Framework:** FastAPI
    * **AI:** PydanticAI
    * **LLMs:** Google Gemini, OpenAI
    * **PDF/Image Processing:** PyMuPDF (fitz), Tesseract (pytesseract), pdf2image
    * **Data Validation:** Pydantic
* **Frontend:**
    * **Core:** HTML5, CSS3, Vanilla JavaScript (ES6+)
    * **Data Grid:** AG Grid Community
* **Deployment:**
    * The app is configured for deployment on Render (see CORS settings in `main.py` and URLs in `app.js`).

##  Setup and Installation

### Prerequisites
* Python 3.8+
* `pip` (Python package installer)
* **Tesseract-OCR:** `pytesseract` requires the Tesseract binary.
    * **macOS:** `brew install tesseract`
    * **Ubuntu:** `sudo apt-get install tesseract-ocr`
    * **Windows:** Download the installer from the [official Tesseract repository](https://github.com/tesseract-ocr/tessdoc).

---

### 1. Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Apex-ace/Bank-statement
    cd statement-extractor
    ```

2.  **Create a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    (A `requirements.txt` based on the project imports)
    ```bash
    pip install fastapi "uvicorn[standard]" python-dotenv "pydantic_ai[google,openai]" PyMuPDF pillow pytesseract pdf2image python-multipart
    ```

4.  **Create your environment file:**
    Create a file named `.env` in the project's root directory and add your API keys.

    **.env.example** (copy this to `.env`):
    ```ini
    # Get your key from [https://aistudio.google.com/](https://aistudio.google.com/)
    GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE

    # (Optional) Get your key from [https://platform.openai.com/](https://platform.openai.com/)
    OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
    ```

5.  **Run the backend server:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The server will be running at `http://127.0.0.1:8000`.

---

### 2. Frontend Setup

The frontend is static and requires no build step.

1.  **Modify the backend URL:**
    For local development, open `app.js` and change the `BACKEND_URL` to point to your local server:

    ```javascript
    // IN: app.js
    // CONFIG: set your backend upload endpoint here
    const BACKEND_URL = window.BACKEND_URL || '[http://127.0.0.1:8000/upload](http://127.0.0.1:8000/upload)'; 
    // ...
    ```

2.  **Serve the frontend:**
    You must serve the `index.html` file from a web server for the JavaScript to run correctly.

    **Easiest way (using Python):**
    In the same directory, run:
    ```bash
    python3 -m http.server 8080
    ```
    Then, open **`http://127.0.0.1:8080`** in your browser.

    (Note: If you are using VS Code, the "Live Server" extension is a great alternative.)

##  API Endpoint

The backend provides one primary endpoint:

### `POST /upload`

Uploads a statement file for extraction.

* **Request Type:** `multipart/form-data`
* **Form Field:** `file` (The PDF or image file)
* **Success Response (200):**
    Returns a `StatementData` JSON object.
    ```json
    {
      "account_holder": "Ayush @Apex-ace",
      "statement_period": "Oct 2025",
      "transactions": [
        {
          "date": "2025-10-01",
          "description": "OPENING BALANCE",
          "amount": 100.0,
          "transaction_type": "Credit",
          "balance": 100.0
        },
        {
          "date": "2025-10-05",
          "description": "COFFEE SHOP",
          "amount": 5.50,
          "transaction_type": "Debit",
          "balance": 94.50
        }
      ]
    }
    ```
* **Error Responses:**
    * **400 (Bad Request):** Invalid file type.
    * **404 (Not Found):** No transactions could be found.
    * **500 (Server Error):** AI error, file processing error, or no LLMs configured.
