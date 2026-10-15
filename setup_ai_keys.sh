#!/bin/bash
# Setup script for AI API keys
# This script configures your .env file with the provided API keys

echo "🥷 SubFluxGPT AI Model Configuration"
echo "===================================="
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
fi

# Add the AI model configurations
echo ""
echo "🤖 Configuring AI Model API Keys..."
echo ""

# Check if AI keys are already in .env
if grep -q "OPENROUTER_API_KEY" .env; then
    echo "⚠️  AI keys already configured in .env"
    echo "To reconfigure, remove the AI section from .env and run this script again"
else
    # Append AI configuration to .env
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

    echo "✅ AI model configuration added to .env"
fi

echo ""
echo "🎯 Configuration Complete!"
echo ""
echo "Your AI models are now configured:"
echo "  - OpenRouter: 12 free models"
echo "  - Mistral: 3 models"
echo "  - Grok (xAI): 1 model"
echo "  - Gemini: 2 models"
echo "  - Total: 18 competing AI models"
echo ""
echo "🚀 To start the live leaderboard monitor:"
echo "  ./subfluxgpt ai-leaderboard"
echo ""
echo "📊 To check AI model statistics:"
echo "  ./subfluxgpt ai-stats"
echo ""
