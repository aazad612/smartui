# Lightweight base image
FROM python:3.11-slim

# Make Python output unbuffered (better logs)
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run will override PORT, but we set a sane default
ENV PORT=8080

# Run as non-root
USER appuser

# Start FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
