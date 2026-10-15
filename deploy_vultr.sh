#!/bin/bash
# SubFluxGPT Automated Vultr VPS Deployment Script
# Run this on your Vultr VPS to automatically deploy SubFluxGPT

set -e

echo "🚀 SubFluxGPT Vultr VPS Deployment"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root. Use: sudo bash deploy_vultr.sh"
    exit 1
fi

# Step 1: Update System
log_info "Updating system..."
apt update && apt upgrade -y

# Step 2: Install Dependencies
log_info "Installing dependencies..."
apt install -y git curl python3 python3-pip python3-venv build-essential libssl-dev libffi-dev python3-dev

# Step 3: Install Docker
log_info "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $USER
    log_info "Docker installed successfully"
else
    log_info "Docker already installed"
fi

# Step 4: Install Docker Compose
log_info "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    log_info "Docker Compose installed successfully"
else
    log_info "Docker Compose already installed"
fi

# Step 5: Clone Repository
log_info "Cloning SubFluxGPT repository..."
if [ ! -d "SubFluxGPT" ]; then
    git clone https://github.com/gitbountyhunter/SubFluxGPT.git
    cd SubFluxGPT
else
    log_warn "SubFluxGPT directory already exists, pulling latest changes..."
    cd SubFluxGPT
    git pull
fi

# Step 6: Configure Environment
log_info "Configuring environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    log_info ".env file created from .env.example"
    log_warn "Please edit .env and add your API keys before starting services"
    log_warn "Run: nano .env"
else
    log_info ".env file already exists"
fi

# Step 7: Add AI Model Configuration
log_info "Adding AI model configuration..."
if ! grep -q "OPENROUTER_API_KEY" .env; then
    cat >> .env << 'EOF'

# ============================================================
# 🥷 AI MODEL CONFIGURATION - 30+ COMPETING AI MODELS
# ============================================================

# OpenRouter API Key
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Primary long-context model
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free

# Free model pool (12 models)
OPENROUTER_MODEL_1=thinkingmachines/inkling-small:free
OPENROUTER_MODEL_2=nvidia/nemotron-3.5-lightning:free
OPENROUTER_MODEL_3=dots-studio/dots-3-note-preview:free
OPENROUTER_MODEL_4=nvidia/nemotron-3-ultra-550b-a55b:free
OPENROUTER_MODEL_5=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
OPENROUTER_MODEL_6=google/gemma-4-31b-it:free
OPENROUTER_MODEL_7=google/gemma-4-26b-a4b-it:free
OPENROUTER_MODEL_8=nvidia/nemotron-3-super-120b-a12b:free
OPENROUTER_MODEL_9=poolside/laguna-s-2.1:free
OPENROUTER_MODEL_10=poolside/laguna-xs-2.1:free
OPENROUTER_MODEL_11=cohere/north-mini-code:free
OPENROUTER_MODEL_12=nvidia/nemotron-3.5-content-safety:free

# Automatic fallback to an available free model
OPENROUTER_FALLBACK_MODEL=openrouter/free

# OpenRouter API base
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Mistral API Key
MISTRAL_API_KEY=your-mistral-api-key-here

# Grok (xAI) API Key
GROK_API_KEY=your-grok-api-key-here

# Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here
EOF
    log_info "AI model configuration added"
else
    log_info "AI model configuration already exists"
fi

# Step 8: Create Directories
log_info "Creating directories..."
mkdir -p data/learning data/self_improving data/monitor
mkdir -p data_collector/storage/raw database models logs
mkdir -p cloud_recon_data benchmarking/results targets

# Step 9: Build Docker Images
log_info "Building Docker images..."
docker-compose build

# Step 10: Start Services
log_info "Starting SubFluxGPT services..."
docker-compose up -d

# Step 11: Wait for services to be healthy
log_info "Waiting for services to be healthy..."
sleep 10

# Step 12: Check Status
log_info "Checking service status..."
docker-compose ps

# Step 13: Configure Firewall
log_info "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 8000/tcp
    ufw allow 8080/tcp
    ufw --force enable
    log_info "Firewall configured"
else
    log_warn "UFW not installed, skipping firewall configuration"
fi

# Step 14: Configure Swap
log_info "Configuring swap (2GB)..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    log_info "Swap configured"
else
    log_info "Swap already configured"
fi

# Step 15: Install Monitoring Tools
log_info "Installing monitoring tools..."
apt install -y htop nload iotop

# Step 16: Print Summary
echo ""
echo "================================================================================"
echo "🎉 SubFluxGPT Deployment Complete!"
echo "================================================================================"
echo ""
echo "Services Running:"
echo "  - PostgreSQL Database: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Inference Server: http://localhost:8000"
echo "  - Monitoring Dashboard: http://localhost:8080"
echo ""
echo "To access from your local machine:"
echo "  ssh -L 8000:localhost:8000 root@$(curl -s ifconfig.me)"
echo "  ssh -L 8080:localhost:8080 root@$(curl -s ifconfig.me)"
echo ""
echo "Then open in browser:"
echo "  http://localhost:8000 - Inference Server"
echo "  http://localhost:8080 - Monitoring Dashboard"
echo ""
echo "Useful Commands:"
echo "  docker-compose ps          - Check service status"
echo "  docker-compose logs -f       - View logs"
echo "  docker-compose restart     - Restart services"
echo "  docker-compose down         - Stop services"
echo "  htop                       - Monitor resources"
echo ""
echo "Documentation:"
echo "  - VULTR_DEPLOYMENT_GUIDE.md"
echo "  - AI_MODEL_SYSTEM.md"
echo "  - DOCKER_SETUP.md"
echo ""
echo "================================================================================"

