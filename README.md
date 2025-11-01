# Statement Extractor

This is a full-stack web application that extracts transaction data from PDF bank statements (both text-based and scanned). It uses a Python backend with **FastAPI** and **PydanticAI** (with Gemini) and a frontend built with **AG-Grid**.

## Features

  * **PDF Upload:** Accepts any PDF file via a simple web interface.
  * **Smart Extraction:** Automatically handles both text-based and scanned (image) PDFs.
  * **AI-Powered Parsing:** Uses **PydanticAI** and Google's **Gemini** model to parse raw text into structured JSON.
  * **Interactive UI:** Displays extracted transactions in a sortable, filterable **AG-Grid** table.
  * **Data Summary:** Calculates and displays total credit and debit amounts.
  * **CSV Export:** Includes a one-click button to export the grid data to CSV.

## 🛠 Tech Stack

  * **Agent Framework:** PydanticAI
  * **LLM:** Google Gemini
  * **Backend:** FastAPI (Python)
  * **Frontend:** HTML, CSS, JavaScript
  * **Data Grid:** AG-Grid (Community)
  * **PDF Processing:** PyMuPDF (text), Tesseract + pdf2image (OCR)

## Demo link: https://statement-extractor-frontend.onrender.com/

## Setup & Installation

### Prerequisites

You must have **Tesseract OCR** installed on your system. This is a system dependency, not a Python package.

  * **macOS (via Homebrew):**
    ```bash
    brew install tesseract
    ```
  * **Ubuntu/Debian:**
    ```bash
    sudo apt-get update
    sudo apt-get install tesseract-ocr
    ```
  * **Windows:**
    Download the installer from the [official Tesseract repository](https://github.com/UB-Mannheim/tesseract/wiki).

### 1\. Backend Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Apex-ace/Bank-statement
    cd pydanticai-statement-extractor/backend
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  
    ```

3.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**

      * Setup `.env`.
      * Edit the `.env` file and add your Google Gemini API key:

    <!-- end list -->

    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```

5.  **Run the backend server:**

    ```bash
    uvicorn app.main:app --reload
    ```

    The server will be running at `http://127.0.0.1:8000`.

### 2\. Frontend Setup

The frontend is a simple static site.

1.  Open a **new terminal** (leave the backend running).
2.  Navigate to the `frontend` directory.
3.  You just need to open the `index.html` file in your web browser.
      * **Recommended:** Use a simple live server for best results (this avoids any potential CORS issues if you deploy).
    <!-- end list -->
    ```bash
    # If you have Python 3
    python -m http.server 8080

    # Or if you have Node.js/npm
    npm install -g live-server
    live-server .
    ```
4.  Open `http://127.0.0.1:8080` (or whatever port your server uses) in your browser.

##  How to Use

1.  Ensure your backend is running on `http://127.0.0.1:8000`.
2.  Open the `index.html` (or your live server URL) in your browser.
3.  Click "Choose File" and select a sample PDF statement from the `samples/` directory or your own.
4.  Click "Process File".
5.  Wait for the loader to finish. The PydanticAI agent call can take 5-15 seconds.
6.  View your structured, filterable transactions in the AG-Grid table\!
7.  Click "Export to CSV" to download the data.

## Disable Adblocker before you access the demo link.
## As this is an prototype uplode file under 2 Mb 
