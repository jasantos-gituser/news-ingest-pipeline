# Use official lightweight Python image
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set Python path for src layout
ENV PYTHONPATH=/app/src

# Copy dependency file first (better Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src ./src

# Test stage (used by CI)
FROM base AS test
ENV CI=true
RUN pip install --no-cache-dir pytest
COPY test ./test
CMD ["pytest", "-q"]

# Runtime stage (your actual app image)
FROM base AS runtime

# Default command
CMD ["uvicorn", "news_ingest_pipeline.api:app", "--host", "0.0.0.0", "--port", "8000"]

# Default command
# CMD ["python", "-m", "news_ingest_pipeline.main"]