FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (FIXED)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY Backend/ .

EXPOSE 7860

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860", "--timeout", "300", "--workers", "1"]