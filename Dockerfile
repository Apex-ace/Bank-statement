# Start with a standard Python 3.11 image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# 1. Install system dependencies (Poppler and Tesseract)
# This is the most important part
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy and install Python requirements
# This assumes your requirements file is in the 'backend' folder
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy your backend application code into the container
# This assumes your Python files are in 'backend/app/'
COPY ./backend/app/ .

# 4. Expose the port Render will use
EXPOSE 10000

# 5. Run the application using Gunicorn (a production server)
# This tells Gunicorn to listen on port 10000 on all interfaces
# It assumes your FastAPI "app" object is in a file named "main.py"
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:10000"]