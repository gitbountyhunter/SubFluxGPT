# SubFluxGPT 🚀

<div align="center">

**A self-generating AI system for continuous bug bounty reconnaissance and model training**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

</div>

---

## 🎯 Overview

SubFluxGPT is a comprehensive AI-powered system that continuously monitors bug bounty platforms, extracts domains/subdomains from disclosed reports, and trains multiple AI models (llama2.c, nanoGPT, GPT-2, and llm.c) for continuous improvement. It features advanced cloud reconnaissance, security tool integration, and benchmarking capabilities.

## ✨ Key Features

### 🤖 Multi-Backend AI Training
- **4 Training Backends**: llama2.c, nanoGPT, GPT-2 (HuggingFace), llm.c (Karpathy's C/CUDA)
- **10+ Model Sizes**: From 15M to 1558M parameters
- **Continuous Learning**: Automatic retraining when new data accumulates
- **Advanced Benchmarking**: Memory tracking, throughput metrics, statistical analysis

### ☁️ Cloud Reconnaissance
- **SNI-IP Range Recon**: Download and process cloud provider IP ranges
- **Enhanced Features**: IP analysis, port scanning, SSL analysis, tech fingerprinting
- **Threat Intelligence**: Shodan/Censys integration for vulnerability data
- **Historical Tracking**: Change detection and trend analysis
- **5 Cloud Providers**: AWS, Google, Azure, DigitalOcean, Oracle

### 🔍 Security Tool Integration
- **20+ Security Tools**: httpx, katana, nuclei, subfinder, amass, and more
- **Integrated Recon Runner**: Orchestrate multiple tools automatically
- **BBRF Support**: Sync results to Bug Bounty Recon Framework
- **Jason Haddix Workflows**: One-liner commands for quick recon

### 📊 Advanced Benchmarking
- **Memory Usage Tracking**: Monitor RAM consumption during inference
- **Throughput Metrics**: Measure tokens per second
- **Statistical Analysis**: Standard deviation, median, min/max for latency
- **Backend Comparison**: Compare performance across all training backends
- **Performance Recommendations**: Automatic optimization suggestions

### 🔧 Developer Features
- **Verbose Mode**: Live updates and detailed logging on all commands
- **REST API**: FastAPI-based inference server
- **Docker Support**: Fully containerized deployment
- **Systemd Services**: 24/7 operation support
- **Comprehensive Documentation**: 3,000+ lines of documentation

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **8GB RAM minimum** (32GB recommended)
- **10GB disk space** (100GB recommended for full system)
- **clang compiler** (for llm.c compilation)

### Installation (5 Minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/SubFluxGPT.git
cd SubFluxGPT

# Install basic dependencies
pip3 install numpy tiktoken psutil

# Verify llm.c binary
ls -lh llm.c/llm.c-master/train_gpt2

# Train your first model (CPU)
python3 training_pipeline/train_llmc.py --model_size 124M --use_gpu=False --verbose

# Start inference server
python3 -m inference.model_server --verbose

# Test it (in another terminal)
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello SubFluxGPT", "model": "gpt2_124M"}'
```

### Full Setup (with PostgreSQL)

```bash
# Install PostgreSQL
brew install postgresql@15  # macOS
# or: sudo apt install postgresql  # Linux

# Create database
createdb subfluxgpt
psql subfluxgpt < database/schema.sql

# Install all dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Run full system
python3 training_pipeline/scheduler.py --verbose
```

---

## 📚 Documentation

### 📖 Essential Guides

1. **[MASTER_COMMAND_GUIDE.md](MASTER_COMMAND_GUIDE.md)** - Complete command reference (986 lines)
   - All SubFluxGPT commands
   - All extra tool commands (20+ security tools)
   - All cloud recon commands
   - Verbose mode usage
   - Complete workflow examples

2. **[MAC_DEPLOYMENT_GUIDE.md](MAC_DEPLOYMENT_GUIDE.md)** - Mac-specific deployment (499 lines)
   - Optimized for Mac (32GB RAM, 8-core)
   - Quick start guide
   - System optimization tips
   - Command cheat sheet
   - Step-by-step learning path

3. **[FINAL_QUALITY_CHECK.md](FINAL_QUALITY_CHECK.md)** - Quality verification (393 lines)
   - A+ quality verification
   - System metrics
   - Deployment readiness
   - Teaching guide

### 📄 Additional Documentation

- **[README.md](README.md)** - This file
- **[SETUP_STATUS.md](SETUP_STATUS.md)** - Current setup status
- **[LLMC_INTEGRATION.md](LLMC_INTEGRATION.md)** - llm.c integration guide
- **[ENHANCED_CLOUD_RECON.md](ENHANCED_CLOUD_RECON.md)** - Cloud recon features
- **[COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md)** - Original command reference
- **[CONTINUOUS_LEARNING.md](CONTINUOUS_LEARNING.md)** - Continuous learning system
- **[EXTERNAL_APIS.md](EXTERNAL_APIS.md)** - External API integration
- **[SECURITY_TOOLS.md](SECURITY_TOOLS.md)** - Security tools documentation
- **[CLOUD_RECON.md](CLOUD_RECON.md)** - Cloud recon documentation
- **[GPT2_INTEGRATION.md](GPT2_INTEGRATION.md)** - GPT-2 integration
- **[HACKERONE_DATASET.md](HACKERONE_DATASET.md)** - Dataset usage
- **[TOOLS_SUMMARY.md](TOOLS_SUMMARY.md)** - Tools summary
- **[REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)** - Review checklist

---

## 💻 Core Commands

### Training Commands

```bash
# llm.c training (CPU)
python3 training_pipeline/train_llmc.py --model_size 124M --use_gpu=False --verbose

# GPT-2 training
python3 training_pipeline/train_gpt2.py --model_size 124M --output_dir ./models/gpt2/124M

# Continuous training scheduler
python3 training_pipeline/scheduler.py --verbose
```

### Inference Commands

```bash
# Start inference server
python3 -m inference.model_server --verbose

# Generate text
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "model": "gpt2_124M"}'

# Analyze domain
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "model": "gpt2_124M"}'
```

### Benchmarking Commands

```bash
# Run benchmark with verbose mode
python3 run_benchmark.py --domain example.com --verbose

# Generate advanced statistical report
python3 run_benchmark.py --domain example.com --verbose --advanced-report

# Compare local backends
python3 run_benchmark.py --domain example.com --compare-backends
```

### Cloud Recon Commands

```bash
# Basic SNI-IP range recon
python3 run_cloud_recon.py --download --process --verbose

# Enhanced recon with killer features
python3 run_cloud_recon.py --enhanced --apex example.com --verbose

# Get Jason Haddix style one-liners
python3 run_cloud_recon.py --one-liners --apex example.com
```

### Security Recon Commands

```bash
# Full reconnaissance
python3 run_recon.py --domain example.com --verbose

# Specific tools
python3 run_recon.py --domain example.com --tools httpx subfinder --verbose

# Sync to BBRF
python3 run_recon.py --domain example.com --sync-bbrf
```

---

## 🏗️ Architecture

```
SubFluxGPT/
├── data_collector/          # Data collection from bug bounty platforms
├── domain_processor/        # Domain extraction and validation
├── training_pipeline/       # Model training (4 backends)
│   ├── prepare_llmc.py      # llm.c data preparation
│   ├── train_llmc.py        # llm.c training wrapper
│   ├── scheduler.py         # Continuous training scheduler
│   └── evaluator.py         # Model evaluation
├── inference/               # Model inference server
│   ├── model_server.py     # FastAPI server
│   └── llmc_inference.py   # llm.c inference wrapper
├── benchmarking/            # Advanced benchmarking system
│   └── benchmark_runner.py # Benchmark runner with metrics
├── cloud_recon/            # Cloud reconnaissance
│   ├── enhanced_cloud_recon.py  # Enhanced features
│   ├── ip_analyzer.py      # IP resolution
│   ├── port_scanner.py     # Port scanning
│   ├── ssl_analyzer.py     # SSL analysis
│   └── tech_fingerprint.py # Technology fingerprinting
├── recon_tools/            # Security tool integration
│   ├── security_tools.py    # Tool orchestrator
│   └── bbrf_client.py      # BBRF integration
├── llm.c/llm.c-master/     # Karpathy's llm.c implementation
├── config.yaml             # Main configuration
├── requirements.txt        # Python dependencies
└── Documentation/          # Comprehensive guides
```

---

## 🎯 Training Backends

### llama2.c
- **Model Sizes**: 15M, 42M, 110M
- **Pros**: Fast inference, custom models
- **Cons**: Requires PyTorch

### nanoGPT
- **Model Sizes**: Custom
- **Pros**: Flexible, educational
- **Cons**: Requires PyTorch

### GPT-2 (HuggingFace)
- **Model Sizes**: 124M, 355M, 774M, 1558M
- **Pros**: Pre-trained weights, high quality
- **Cons**: Requires PyTorch + Transformers

### llm.c (Karpathy's C/CUDA)
- **Model Sizes**: 124M, 350M, 774M, 1558M
- **Pros**: ~7% faster than PyTorch, minimal dependencies
- **Cons**: Primarily for training, inference limited

---

## ☁️ Cloud Recon Features

### 1. IP Resolution and ASN Lookup
- Cloud provider detection (AWS, Google, Azure, DigitalOcean, Oracle)
- Geolocation data (country, city, region)
- Organizational data (ISP, organization name)

### 2. Port Scanning
- 21 common service ports
- Service identification (HTTP, SSH, MySQL, Redis, etc.)
- Banner grabbing
- Service categorization

### 3. SSL/TLS Certificate Analysis
- Expiration tracking
- Self-signed detection
- Wildcard certificate identification
- SAN (Subject Alternative Names) extraction

### 4. Technology Fingerprinting
- Web server identification (nginx, Apache, IIS)
- Framework detection (Django, Flask, Express, Rails)
- CDN detection (Cloudflare, Akamai, Fastly)
- Load balancer detection

### 5. Threat Intelligence
- Shodan API integration
- Censys API integration
- Vulnerability tracking with CVE IDs
- Risk scoring

### 6. Historical Tracking
- Timestamped snapshots
- Change detection
- New domain discovery
- Trend analysis

---

## 🔧 Security Tools (20+)

- **httpx** - HTTP probing
- **katana** - Web crawling
- **nuclei** - Vulnerability scanning
- **subfinder** - Subdomain discovery
- **amass** - Attack surface discovery
- **naabu** - Port scanning
- **dnsx** - DNS resolution
- **gau** - Wayback URL retrieval
- **waybackurls** - Wayback machine URLs
- **hakrawler** - Web crawling
- **assetfinder** - Domain discovery
- **ffuf** - Web fuzzing
- **feroxbuster** - Directory discovery
- **arjun** - Parameter discovery
- **subjs** - JavaScript analysis
- **anew** - Deduplication
- And 6+ more tools

---

## 📊 Benchmarking Metrics

- **Latency**: Generation time in milliseconds
- **Memory Usage**: RAM consumption in MB
- **Throughput**: Tokens per second
- **Token Count**: Prompt and generated tokens
- **Statistical Analysis**: Std dev, median, min/max
- **Backend Comparison**: Performance across backends
- **Recommendations**: Automatic optimization suggestions

---

## 🔍 Verbose Mode

All major commands support verbose mode with `--verbose` flag:

```bash
python3 training_pipeline/scheduler.py --verbose
python3 run_benchmark.py --domain example.com --verbose
python3 run_cloud_recon.py --enhanced --apex example.com --verbose
python3 run_recon.py --domain example.com --verbose
python3 -m inference.model_server --verbose
```

**Verbose mode shows:**
- Real-time progress updates
- Detailed memory usage
- Token-by-token generation
- Network request details
- Error stack traces

---

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f collector
docker-compose logs -f trainer
docker-compose logs -f inference

# Access monitoring dashboard
http://localhost:8080

# Access inference API
http://localhost:8000
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

- **Database settings**: PostgreSQL connection
- **Platform configurations**: API keys and platform-specific settings
- **Data collection**: Intervals, rate limits, storage limits
- **Domain processing**: Validation methods, DNS settings
- **Training**: Model sizes, hyperparameters, triggers
- **Inference**: Server settings, generation parameters
- **Benchmarking**: Metrics collection, comparison settings
- **Cloud Recon**: Provider selection, feature toggles
- **Security Tools**: Tool enablement, configuration

---

## 📈 Performance Expectations

### Training Times (CPU, 8-core Mac)
- **124M model (llm.c)**: 1-2 hours
- **350M model (llm.c)**: 4-6 hours
- **124M model (GPT-2)**: 2-3 hours
- **42M model (llama2.c)**: 30-60 minutes

### Inference Speed
- **124M model**: ~50-100ms per generation
- **350M model**: ~100-200ms per generation
- **Tokens/second**: ~20-50 tokens/sec (CPU)

### Memory Usage
- **124M model training**: ~4-8GB RAM
- **350M model training**: ~8-16GB RAM
- **Inference server**: ~2-4GB RAM
- **Total with all features**: ~16-24GB RAM

---

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/SubFluxGPT.git
cd SubFluxGPT

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run linting
flake8 .
black .
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## ⚠️ Disclaimer

This tool is for educational and authorized security testing purposes only. Always obtain proper authorization before testing any systems. The authors are not responsible for any misuse of this software.

---

## 🙏 Acknowledgments

- **Andrej Karpathy** for [llm.c](https://github.com/karpathy/llm.c)
- **Jason Haddix** for reconnaissance methodologies
- **Bug Bounty Community** for inspiration and feedback

---

## 📞 Support

- **Documentation**: See [MASTER_COMMAND_GUIDE.md](MASTER_COMMAND_GUIDE.md)
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

---

## 🎉 Status

**System Status**: ✅ A+ Quality - Production Ready

- ✅ All code compiles without errors
- ✅ llm.c integrated and compiled
- ✅ Benchmarking active for all models
- ✅ Advanced features implemented
- ✅ Verbose mode enabled
- ✅ Comprehensive documentation
- ✅ Ready for deployment

---

<div align="center">

**Built with ❤️ for the bug bounty community**

[⭐ Star us on GitHub](https://github.com/yourusername/SubFluxGPT)

</div>
