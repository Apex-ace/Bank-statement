# Start from an official Python image
FROM python:3.11-slim

# Set a working directory inside the container
WORKDIR /app

# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the rest of your application code
COPY ./app ./app

# 4. Expose the port your app will run on

EXPOSE 8000

# 5. Define the command to run your app
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT