#!/bin/bash
# SubFluxGPT Setup Script
# This script sets up the environment and verifies the installation

set -e

echo "========================================"
echo "SubFluxGPT Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    python configure_apis.py --create-env
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data
mkdir -p data/bugbounty_tokens
mkdir -p data/hackerone_tokens
mkdir -p data/hackerone_gpt2_tokens
mkdir -p models/checkpoints
mkdir -p models/llama2c
mkdir -p models/gpt2
mkdir -p models/nanogpt
mkdir -p benchmarking/results
mkdir -p logs

# Verify imports
echo ""
echo "Verifying module imports..."
python3 -c "from external_apis import MultiAPIClient; print('✓ external_apis')"
python3 -c "from benchmarking import BenchmarkResult; print('✓ benchmarking')"
python3 -c "import yaml; print('✓ yaml')"
python3 -c "import sys; sys.path.insert(0, '.'); from training_pipeline.train_gpt2 import GPT2Trainer; print('✓ train_gpt2')"
python3 -c "import sys; sys.path.insert(0, '.'); from inference.model_server import app; print('✓ model_server')"

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env to add your API keys"
echo "2. Edit config.yaml to enable desired providers"
echo "3. Run: python configure_apis.py --list"
echo "4. Prepare data: python training_pipeline/prepare_hackerone.py --tokenizer=both"
echo "5. Train models: python training_pipeline/train_gpt2.py --model_size 124M"
echo "6. Start server: python -m inference.model_server"
echo ""
