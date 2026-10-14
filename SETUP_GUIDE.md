# SubFluxGPT - Quick Setup Guide

## Status: ✅ Ready to Run

All code has been reviewed, fixed, and verified. SubFluxGPT is ready to run perfectly!

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/beanman/Documents/Desktop/SubFluxGPT
bash setup.sh
```

This will:
- Create a virtual environment
- Install all required packages
- Create necessary directories
- Verify module imports

### 2. Configure API Keys (Optional - for external APIs)

```bash
python3 configure_apis.py --create-env
```

Then edit `.env` to add your API keys:

```bash
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
COHERE_API_KEY=your-key-here
```

### 3. Prepare Training Data

```bash
# For llama2.c models
python3 training_pipeline/prepare_hackerone.py --tokenizer=llama2c

# For GPT-2 models
python3 training_pipeline/prepare_hackerone.py --tokenizer=gpt2

# For both
python3 training_pipeline/prepare_hackerone.py --tokenizer=both
```

### 4. Train Models

```bash
# Train GPT-2 model
python3 training_pipeline/train_gpt2.py --model_size 124M

# Or run continuous training scheduler
python3 training_pipeline/scheduler.py
```

### 5. Start Inference Server

```bash
python3 -m inference.model_server
```

Server will run on: `http://localhost:8000`

### 6. Run Benchmarks

```bash
python3 run_benchmark.py --domain example.com --compare
```

## What's Included

### Model Architectures
- ✅ **llama2.c**: 15M, 42M, 110M models
- ✅ **nanoGPT**: Custom sizes
- ✅ **GPT-2**: 124M, 355M, 774M, 1558M models

### Data Sources
- ✅ HackerOne disclosed reports (HuggingFace)
- ✅ Local database (PostgreSQL)
- ✅ Dual tokenizer support (SentencePiece + tiktoken)

### External API Integration
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ Anthropic (Claude 3)
- ✅ Cohere (Command)
- ✅ Google (Gemini) - optional
- ✅ Easy to add more providers

### Benchmarking System
- ✅ Compare local vs external models
- ✅ Track latency and context windows
- ✅ Save results for growth tracking
- ✅ Auto-run on domain analysis

## Key Files

### Configuration
- `config.yaml` - Main configuration
- `.env` - API keys (create from template)
- `requirements.txt` - Python dependencies

### Training
- `training_pipeline/train_gpt2.py` - GPT-2 training
- `training_pipeline/scheduler.py` - Continuous training
- `training_pipeline/prepare_hackerone.py` - Data preparation

### Inference
- `inference/model_server.py` - FastAPI inference server
- `external_apis/api_client.py` - External API clients
- `benchmarking/benchmark_runner.py` - Benchmarking system

### Scripts
- `setup.sh` - One-time setup
- `configure_apis.py` - API key configuration
- `run_benchmark.py` - Run benchmarks

### Documentation
- `README.md` - Project overview
- `QUICKSTART.md` - Quick start guide
- `GPT2_INTEGRATION.md` - GPT-2 integration details
- `HACKERONE_DATASET.md` - Dataset documentation
- `EXTERNAL_APIS.md` - External API guide
- `REVIEW_CHECKLIST.md` - Code review and fixes

## API Endpoints

### Generate Text
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze example.com",
    "model": "gpt2_124M",
    "max_new_tokens": 256
  }'
```

### Analyze Domain
```bash
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "model": "gpt2_124M",
    "run_benchmark": true
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Model Growth Tracking

Every time you analyze a domain with `run_benchmark=true`, the system:
1. Analyzes with your local model
2. Runs benchmark with all external APIs
3. Compares performance metrics
4. Saves results to `benchmarking/results/`

Track your model's growth over time by comparing benchmark results!

## Troubleshooting

### Module Not Found Errors
Run: `bash setup.sh` to install dependencies

### API Key Errors
Run: `python3 configure_apis.py --list` to verify keys are set

### Data Preparation Errors
Ensure you've run: `python3 training_pipeline/prepare_hackerone.py --tokenizer=both`

### Training Errors
Check that data files exist in `data/hackerone_tokens/` or `data/hackerone_gpt2_tokens/`

## Next Steps

1. ✅ Run `bash setup.sh` to install dependencies
2. ✅ Configure API keys in `.env` (optional)
3. ✅ Prepare data with `prepare_hackerone.py`
4. ✅ Train your first model
5. ✅ Start the inference server
6. ✅ Run benchmarks to track growth

## Support

For issues or questions:
- Check the documentation files in the project root
- Review `REVIEW_CHECKLIST.md` for code changes
- See `EXTERNAL_APIS.md` for API integration help

---

**SubFluxGPT is ready to train your own AI models and benchmark them against the best external APIs!** 🚀
