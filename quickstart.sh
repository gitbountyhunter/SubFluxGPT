#!/bin/bash
# Quick start script for SubFluxGPT

echo "🚀 SubFluxGPT Quick Start"
echo "=========================="
echo ""

# Check Python version
echo "[*] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "    Found Python $python_version"

# Create virtual environment
echo ""
echo "[*] Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "[*] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install package in development mode
echo ""
echo "[*] Installing SubFluxGPT..."
pip install -e .

# Setup .env file
echo ""
echo "[*] Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "    Created .env file from template"
    echo "    ⚠️  Please edit .env and add your API keys!"
else
    echo "    .env file already exists"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys (at least GEMINI_API_KEY)"
echo "2. Run: subfluxgpt --help"
echo "3. Try: subfluxgpt -i your_subs.txt -o output.txt --api gemini"
echo ""
echo "For more examples, see EXAMPLES.md"
