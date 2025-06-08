FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 build-essential gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8881

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8881"]
