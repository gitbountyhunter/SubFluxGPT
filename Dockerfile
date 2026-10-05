FROM python:3.11-slim

LABEL maintainer="your.email@example.com"
LABEL description="SubFluxGPT - AI-powered subdomain enumeration"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/
COPY setup.py pyproject.toml ./

# Install package
RUN pip install -e .

# Create directory for input/output
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["subfluxgpt", "--help"]
