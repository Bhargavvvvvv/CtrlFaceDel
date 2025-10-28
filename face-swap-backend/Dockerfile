# Use full Debian base with Python
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for OpenCV + InsightFace build
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
