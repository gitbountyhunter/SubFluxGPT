# Multi-stage Dockerfile for SubFluxGPT
FROM python:3.10-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    make \
    wget \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch with CPU support (use CUDA version if GPU available)
# For GPU support, uncomment the line below and comment the CPU version
# RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data_collector/storage/raw \
    database \
    models \
    logs \
    data/learning \
    data/self_improving \
    data/monitor \
    cloud_recon_data \
    benchmarking/results

# Make scripts executable
RUN chmod +x subfluxgpt \
    run_cloud_recon.py \
    run_recon.py \
    run_benchmark.py \
    bug_bounty_monitor.py \
    self_improving_llm.py \
    unsloth_finetuner.py \
    setup.sh

# Expose ports for inference server and monitoring
EXPOSE 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Default command - run the CLI interface
CMD ["./subfluxgpt"]
