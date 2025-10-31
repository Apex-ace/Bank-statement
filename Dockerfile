# -----------------------------------------------------------------
# STAGE 1: Build the environment
# -----------------------------------------------------------------
# Use an official Python 3.11 image
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Install System Dependencies ---
# We need to install Tesseract OCR and its dependencies
RUN apt-get update \
    && apt-get install -y \
       tesseract-ocr \
       libtesseract-dev \
       libleptonica-dev \
       pkg-config \
    # Install Poppler for pdf2image
       poppler-utils \
    # Clean up apt cache
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# --- Install Python Dependencies ---
# Copy ONLY the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt \
    && pip install --no-cache /app/wheels/*

# -----------------------------------------------------------------
# STAGE 2: Run the application
# -----------------------------------------------------------------
# Copy the rest of your application code
COPY . .

# --- Expose Port & Run ---
# Render will automatically inject the PORT environment variable.
# We will run Uvicorn on 0.0.0.0 to listen on all interfaces.
# The $PORT variable will be supplied by Render.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]

# Note: Render's health check will fail if you use $PORT, 
# so we hardcode 10000. Render will still map its external port 
# to your container's 10000 port.
