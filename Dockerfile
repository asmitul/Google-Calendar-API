# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
COPY app/ ./app/

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8009
EXPOSE 8009

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]