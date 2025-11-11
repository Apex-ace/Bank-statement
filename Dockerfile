FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./backend/app/ .

EXPOSE 10000
CMD gunicorn -k uvicorn.workers.UvicornWorker --timeout 200 -b 0.0.0.0:$PORT main:app
