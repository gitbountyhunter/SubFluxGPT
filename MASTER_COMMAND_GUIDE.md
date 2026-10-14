# SubFluxGPT - Master Command Guide

Complete reference for all SubFluxGPT commands, tools, and features.

## Table of Contents
1. [Core System Commands](#core-system-commands)
2. [Training Commands](#training-commands)
3. [Inference Commands](#inference-commands)
4. [Benchmarking Commands](#benchmarking-commands)
5. [Cloud Recon Commands](#cloud-recon-commands)
6. [Security Tool Commands](#security-tool-commands)
7. [Data Collection Commands](#data-collection-commands)
8. [Configuration Commands](#configuration-commands)
9. [Verbose Mode Usage](#verbose-mode-usage)

---

## Core System Commands

### Setup and Installation

```bash
# Run the setup script (recommended)
bash setup.sh

# Manual installation
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p data/bugbounty_tokens data/hackerone_tokens data/hackerone_gpt2_tokens
mkdir -p models/checkpoints models/llama2c models/gpt2 models/nanogpt models/llmc
mkdir -p benchmarking/results logs metrics cloud_recon_data
```

### API Key Configuration

```bash
# Create .env template
python3 configure_apis.py --create-env

# List configured API keys
python3 configure_apis.py --list

# Edit .env file manually
nano .env
# or
vim .env
```

### Database Setup

```bash
# Create PostgreSQL database
createdb subfluxgpt

# Initialize database schema
psql subfluxgpt < database/schema.sql

# Or use Docker
docker run -d \
  --name subfluxgpt-db \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=subfluxgpt \
  -p 5432:5432 \
  postgres:15
```

---

## Training Commands

### Data Preparation

#### Prepare HackerOne Data for llama2.c
```bash
# Prepare with SentencePiece tokenizer
python3 training_pipeline/prepare_hackerone.py --tokenizer=llama2c

# Prepare with custom vocabulary size
python3 training_pipeline/prepare_hackerone.py --tokenizer=llama2c --vocab_size 2048

# Prepare with custom train/val split
python3 training_pipeline/prepare_hackerone.py --tokenizer=llama2c --train_split 0.8
```

#### Prepare HackerOne Data for GPT-2
```bash
# Prepare with tiktoken tokenizer
python3 training_pipeline/prepare_hackerone.py --tokenizer=gpt2

# Prepare for both tokenizers
python3 training_pipeline/prepare_hackerone.py --tokenizer=both
```

#### Prepare Database Data
```bash
# Prepare for llama2.c
python3 training_pipeline/prepare_bugbounty.py --vocab_size 4096

# Prepare for llm.c
python3 training_pipeline/prepare_llmc.py --limit 10000 --val_split 0.1
```

#### Prepare for nanoGPT
```bash
python3 training_pipeline/prepare_hackerone_nanogpt.py
```

### Model Training

#### GPT-2 Training (HuggingFace)
```bash
# Train GPT-2 Small (124M)
python3 training_pipeline/train_gpt2.py --model_size 124M --output_dir ./models/gpt2/124M

# Train GPT-2 Medium (355M)
python3 training_pipeline/train_gpt2.py --model_size 355M --output_dir ./models/gpt2/355M

# Train GPT-2 Large (774M)
python3 training_pipeline/train_gpt2.py --model_size 774M --output_dir ./models/gpt2/774M

# Train GPT-2 XL (1558M)
python3 training_pipeline/train_gpt2.py --model_size 1558M --output_dir ./models/gpt2/1558M
```

#### llm.c Training (Karpathy's C/CUDA)
```bash
# Train 124M model with CPU
python3 training_pipeline/train_llmc.py --model_size 124M --use_gpu=False

# Train 124M model with GPU (CUDA)
python3 training_pipeline/train_llmc.py --model_size 124M --use_gpu

# Train 350M model with GPU
python3 training_pipeline/train_llmc.py --model_size 350M --use_gpu

# Compile only (no training)
python3 training_pipeline/train_llmc.py --compile_only --use_gpu

# Train with verbose mode
python3 training_pipeline/train_llmc.py --model_size 124M --use_gpu --verbose
```

#### llama2.c Training
```bash
# Train 15M model
python3 llama2.c/train.py --batch_size 16 --learning_rate 5e-4 --max_iters 100000

# Train 42M model
python3 llama2.c/train.py --dim 512 --n_layers 8 --n_heads 8 --batch_size 16

# Train 110M model
python3 llama2.c/train.py --dim 768 --n_layers 12 --n_heads 12 --batch_size 16
```

#### nanoGPT Training
```bash
# Train with HackerOne configuration
python3 config/finetune_hackerone.py

# Train with custom configuration
python3 nanoGPT/train.py config/train_hackerone.py
```

### Training Scheduler (Continuous Training)

```bash
# Run training scheduler (automatic training when 1000+ new reports)
python3 training_pipeline/scheduler.py

# Run with verbose mode (live updates)
python3 training_pipeline/scheduler.py --verbose

# Run with custom config
python3 training_pipeline/scheduler.py --config custom_config.yaml
```

### Model Evaluation

```bash
# Evaluate a specific model
python3 training_pipeline/evaluator.py --model gpt2_124M --type gpt2

# Compare multiple models
python3 training_pipeline/evaluator.py --compare llama2c_42M gpt2_355M llmc_350M

# Generate evaluation report
python3 training_pipeline/evaluator.py --report
```

---

## Inference Commands

### Start Inference Server

```bash
# Start with default configuration
python3 -m inference.model_server

# Start with custom host/port
python3 -m inference.model_server --host 0.0.0.0 --port 8000

# Start with custom workers
python3 -m inference.model_server --workers 4

# Start with verbose mode
python3 -m inference.model_server --verbose
```

### Inference API Usage

#### Generate Text
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze example.com for subdomain takeover vulnerabilities",
    "model": "gpt2_124M",
    "max_new_tokens": 256,
    "temperature": 0.8,
    "top_p": 0.9
  }'
```

#### Analyze Domain
```bash
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "model": "gpt2_124M"
  }'
```

#### Analyze Domain with Benchmark
```bash
curl -X POST http://localhost:8000/analyze_domain?run_benchmark=true \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "model": "gpt2_124M"
  }'
```

#### Health Check
```bash
curl http://localhost:8000/health
```

---

## Benchmarking Commands

### Run Benchmarks

```bash
# Run benchmark for a domain
python3 run_benchmark.py --domain example.com

# Run benchmark with comparison
python3 run_benchmark.py --domain example.com --compare

# Run with verbose mode (live updates)
python3 run_benchmark.py --domain example.com --verbose

# Run with custom output
python3 run_benchmark.py --domain example.com --output benchmarking/results/example.json

# Run with custom config
python3 run_benchmark.py --domain example.com --config custom_config.yaml

# Compare local backends (llama2.c, nanoGPT, GPT-2, llm.c)
python3 run_benchmark.py --domain example.com --compare-backends

# Generate advanced statistical report
python3 run_benchmark.py --domain example.com --advanced-report
```

### Benchmark Analysis

```bash
# View latest results
cat benchmarking/results/latest.json

# View advanced report
cat benchmarking/results/example_advanced_report.json

# Compare results over time
python3 -c "import json; data=json.load(open('benchmarking/results/latest.json')); print(json.dumps(data, indent=2))"
```

### Advanced Benchmarking Features

The benchmarking system now includes:
- **Memory Usage Tracking**: Tracks memory consumption during inference
- **Throughput Metrics**: Measures tokens per second
- **Statistical Analysis**: Standard deviation, median, min/max for latency
- **Backend Comparison**: Compares llama2.c, nanoGPT, GPT-2, and llm.c performance
- **Recommendations**: Automatic performance recommendations based on results

---

## Cloud Recon Commands

### Basic Cloud Recon (SNI-IP Ranges)

```bash
# Download and process all providers
python3 run_cloud_recon.py --download --process

# Filter by specific apex domain
python3 run_cloud_recon.py --download --process --apex dell.com

# Export for BountyCatch
python3 run_cloud_recon.py --export --project dell_recon

# Get one-liner commands (Jason Haddix style)
python3 run_cloud_recon.py --one-liners --apex dell.com

# Full workflow with AI analysis
python3 run_cloud_recon.py --full --apex dell.com --project dell_recon --ai
```

### Enhanced Cloud Recon (Killer Features)

```bash
# Run all killer features
python3 run_cloud_recon.py --enhanced --apex dell.com --project dell_recon

# Run with verbose mode
python3 run_cloud_recon.py --enhanced --apex dell.com --project dell_recon --verbose

# Run specific features only
python3 run_cloud_recon.py --enhanced --no-port --no-ssl --apex dell.com

# Enable threat intelligence (requires API keys)
python3 run_cloud_recon.py --enhanced --threat-intel --apex dell.com

# Disable specific features
python3 run_cloud_recon.py --enhanced --no-ip --apex dell.com  # No IP analysis
python3 run_cloud_recon.py --enhanced --no-port --apex dell.com  # No port scanning
python3 run_cloud_recon.py --enhanced --no-ssl --apex dell.com  # No SSL analysis
python3 run_cloud_recon.py --enhanced --no-tech --apex dell.com  # No tech fingerprinting
```

### Cloud Recon Features

#### 1. IP Resolution and ASN Lookup
- Resolves domains to IP addresses
- ASN lookup using ipinfo.io API
- Cloud provider detection (AWS, Google, Azure, DigitalOcean, Oracle)
- Geolocation data (country, city, region)
- Organizational data (ISP, organization name)

#### 2. Port Scanning
- Multi-port scanning across 21 common service ports
- Parallel scanning for speed
- Service identification (HTTP, SSH, MySQL, Redis, etc.)
- Banner grabbing
- Service categorization

#### 3. SSL/TLS Certificate Analysis
- Certificate extraction from HTTPS endpoints
- Expiration tracking with days-until-expiry
- Issuer identification
- Self-signed detection
- Wildcard certificate identification
- SAN (Subject Alternative Names) extraction
- Signature algorithm and key size analysis

#### 4. Technology Fingerprinting
- HTTP header analysis for technology detection
- Web server identification (nginx, Apache, IIS, etc.)
- Framework detection (Django, Flask, Express, Rails, Laravel)
- CDN detection (Cloudflare, Akamai, Fastly, CloudFront)
- Load balancer detection (AWS ELB/ALB, HAProxy, nginx)
- Cloud infrastructure identification

#### 5. Threat Intelligence Integration
- Shodan API integration for vulnerability data
- Censys API integration for service enumeration
- Vulnerability tracking with CVE IDs
- Service enumeration from threat intel
- Risk scoring based on open ports and vulnerabilities

#### 6. Historical Tracking
- Timestamped snapshots of all scans
- Change detection between scans
- New domain discovery tracking
- Domain removal tracking
- Trend analysis over time

---

## Security Tool Commands

### HTTPX (HTTP Toolkit)
```bash
# Probe domains for alive web servers
echo -e "example.com\ntest.com" | httpx -silent -json -status-code -title

# Crawl URLs
httpx -u https://example.com -silent -json -scrape -depth 2

# With custom options
httpx -silent -json -timeout 10 -threads 50
```

### Katana (Web Crawler)
```bash
# Crawl a URL
katana -u https://example.com -silent -json -depth 2 -js-crawl

# Crawl with rate limiting
katana -u https://example.com -silent -json -rate-limit 10

# Crawl from file
katana -list urls.txt -silent -json -depth 3
```

### Anew (Deduplication)
```bash
# Deduplicate domains
echo -e "example.com\ntest.com\nexample.com" | anew domains.txt

# Deduplicate URLs
cat urls.txt | anew deduped_urls.txt
```

### GAU (GetAllUrls)
```bash
# Get URLs from wayback machine
gau example.com --subs --threads 5

# Get URLs with blacklist
gau example.com --subs --blacklist "(css|js|png|jpg)"

# Get URLs for multiple domains
cat domains.txt | gau --subs --threads 10
```

### Nuclei (Vulnerability Scanner)
```bash
# Scan a URL
nuclei -u https://example.com -silent -json -severity medium,high,critical

# Scan multiple targets
cat targets.txt | nuclei -silent -json -severity critical

# Scan with custom templates
nuclei -u https://example.com -templates cves/ -silent -json

# Scan with rate limiting
nuclei -u https://example.com -rate-limit 100 -silent -json
```

### Naabu (Port Scanner)
```bash
# Scan top ports
echo "example.com" | naabu -silent -json -top-ports 1000

# Scan specific ports
echo "example.com" | naabu -silent -json -ports 80,443,8080

# Scan with rate limiting
echo "example.com" | naabu -silent -json -rate-limit 1000
```

### DNSX (DNS Toolkit)
```bash
# Resolve domains
echo -e "example.com\ntest.com" | dnsx -silent -json -a -aaaa

# Resolve with custom resolver
echo "example.com" | dnsx -silent -json -r 8.8.8.8

# DNS wildcard detection
echo "example.com" | dnsx -silent -json -w
```

### Amass (Attack Surface Discovery)
```bash
# Enumerate subdomains (passive)
amass enum -passive -d example.com -json

# Enumerate subdomains (active)
amass enum -active -d example.com -json

# Gather intelligence
amass intel -d example.com -json

# With timeout
amass enum -passive -d example.com -timeout 300 -json

# Include unresolvable names
amass enum -passive -d example.com -include-unresolvable -json
```

### Hakrawler (Web Crawler)
```bash
# Crawl a URL
echo "https://example.com" | hakrawler -depth 3

# Crawl with subdomains
echo "https://example.com" | hakrawler -depth 3 -subs

# Crawl with scope
echo "https://example.com" | hakrawler -depth 3 -scope rdn

# Crawl from file
cat urls.txt | hakrawler -depth 5
```

### Waybackurls (Wayback Machine URLs)
```bash
# Get URLs for domain
waybackurls example.com

# Get URLs without subdomains
waybackurls example.com -no-subs

# Get URLs for multiple domains
cat domains.txt | waybackurls
```

### Subfinder (Subdomain Discovery)
```bash
# Enumerate subdomains
subfinder -d example.com -silent

# Enumerate with all sources
subfinder -d example.com -all -silent

# Enumerate with JSON output
subfinder -d example.com -json -silent

# Enumerate with custom threads
subfinder -d example.com -threads 20 -silent
```

### Assetfinder (Domain Discovery)
```bash
# Find domains and subdomains
assetfinder --subs-only example.com

# Find with ignore pattern
assetfinder --subs-only example.com --ignore '*.test.com'

# Find from file
cat domains.txt | assetfinder --subs-only
```

### Crt.sh (Certificate Transparency)
```bash
# Query via curl (no install needed)
curl -s "https://crt.sh/?q=%.example.com&output=json" | jq -r '.[].name_value' | sort -u
```

### FFUF (Web Fuzzer)
```bash
# Fuzz directories
ffuf -u http://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt

# Fuzz with extensions
ffuf -u http://example.com/FUZZ -w wordlist.txt -e php,html,js

# Fuzz with status codes
ffuf -u http://example.com/FUZZ -w wordlist.txt -mc 200,301,302

# Fuzz with threads
ffuf -u http://example.com/FUZZ -w wordlist.txt -t 100
```

### Feroxbuster (Directory Discovery)
```bash
# Scan for directories
feroxbuster -u http://example.com -w /usr/share/wordlists/dirb/common.txt

# Scan with extensions
feroxbuster -u http://example.com -w wordlist.txt -x php,html,js

# Scan with depth
feroxbuster -u http://example.com -w wordlist.txt -d 5

# Scan with threads
feroxbuster -u http://example.com -w wordlist.txt -t 50
```

### Arjun (Parameter Discovery)
```bash
# Discover parameters
arjun -u https://example.com/page?id=1

# Discover with headers
arjun -u https://example.com/page -d "Authorization: Bearer token"

# Discover with POST data
arjun -u https://example.com/api -d '{"data":"test"}'
```

### Subjs (JavaScript Analysis)
```bash
# Extract subdomains from JS files
cat js_urls.txt | subjs

# Extract from multiple URLs
echo -e "https://example.com/app.js\nhttps://example.com/main.js" | subjs
```

### Integrated Recon Runner

```bash
# Run full reconnaissance
python3 run_recon.py --domain example.com

# Run with verbose mode
python3 run_recon.py --domain example.com --verbose

# Run specific tools
python3 run_recon.py --domain example.com --tools httpx subfinder

# Sync results to BBRF
python3 run_recon.py --domain example.com --sync-bbrf

# Custom output file
python3 run_recon.py --domain example.com --output custom_results.json
```

---

## Data Collection Commands

### Collect Bug Bounty Reports

```bash
# Run data collection from all platforms
python3 -m data_collector.main

# Collect from specific platform
python3 -m data_collector.main --platform hackerone

# Collect with limit
python3 -m data_collector.main --limit 100
```

### Configure Platforms

Edit `config.yaml` to enable/disable platforms:

```yaml
platforms:
  hackerone:
    enabled: true
    api_key: ${HACKERONE_API_KEY:-}
    use_dataset: true
    dataset_id: "Hacker0x01/hackerone_disclosed_reports"
  
  bugcrowd:
    enabled: true
    api_token: ${BUGCROWD_API_TOKEN:-}
  
  yeswehack:
    enabled: true
    api_key: ${YESWEHACK_API_KEY:-}
```

---

## Configuration Commands

### View Configuration

```bash
# View full config
cat config.yaml

# View specific section (requires pyyaml)
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml'))['training'])"

# Validate config
python3 -c "import yaml; yaml.safe_load(open('config.yaml')); print('Config valid')"
```

### Update Configuration

```bash
# Edit config
nano config.yaml
# or
vim config.yaml

# Update specific section (requires pyyaml)
python3 -c "
import yaml
config = yaml.safe_load(open('config.yaml'))
config['training']['gpt2']['batch_size'] = 8
with open('config.yaml', 'w') as f:
    yaml.dump(config, f)
"
```

### Configuration Sections

#### Database Configuration
```yaml
database:
  url: ${DATABASE_URL:-postgresql://subflux:changeme@localhost:5432/subfluxgpt}
  pool_size: 10
  max_overflow: 20
```

#### Training Configuration
```yaml
training:
  model_sizes:
    - 15M
    - 42M
    - 110M
  min_new_reports: 1000
  max_reports_per_batch: 10000
```

#### Inference Configuration
```yaml
inference:
  host: 0.0.0.0
  port: 8000
  workers: 4
  default_model: llama2c_42M
```

#### Benchmarking Configuration
```yaml
benchmarking:
  enabled: true
  output_dir: ./benchmarking/results
  auto_run_on_domain_analysis: true
  compare_local_vs_external: true
```

#### Cloud Recon Configuration
```yaml
cloud_recon:
  enabled: true
  output_dir: ./cloud_recon_data
  providers:
    - amazon
    - digitalocean
    - google
    - microsoft
    - oracle
```

---

## Verbose Mode Usage

Verbose mode provides live updates and detailed logging for all commands.

### Enable Verbose Mode

Most commands support the `--verbose` or `-v` flag:

```bash
# Training with verbose mode
python3 training_pipeline/scheduler.py --verbose
python3 training_pipeline/train_llmc.py --model_size 124M --verbose

# Benchmarking with verbose mode
python3 run_benchmark.py --domain example.com --verbose

# Cloud recon with verbose mode
python3 run_cloud_recon.py --enhanced --apex dell.com --verbose

# Security recon with verbose mode
python3 run_recon.py --domain example.com --verbose

# Inference server with verbose mode
python3 -m inference.model_server --verbose
```

### What Verbose Mode Shows

- **Real-time progress updates** during training and benchmarking
- **Detailed memory usage** information
- **Token-by-token generation** progress
- **Network request details** for API calls
- **Error stack traces** with full context
- **Performance metrics** as they're calculated

### Verbose Output Example

```
[VERBOSE] Starting benchmark for local model: gpt2_124M
[VERBOSE] Loading model: gpt2_124M
[VERBOSE] Prompt tokens: 45
[VERBOSE] Using CUDA GPU
[VERBOSE] Generated 256 tokens (total: 301)
[VERBOSE] Latency: 1234.56ms, Memory: 45.67MB, Tokens/sec: 207.89
```

---

## Complete Workflow Examples

### Full Training Workflow

```bash
# 1. Prepare data
python3 training_pipeline/prepare_hackerone.py --tokenizer=both --verbose

# 2. Train models with verbose mode
python3 training_pipeline/train_gpt2.py --model_size 124M
python3 training_pipeline/train_llmc.py --model_size 124M --verbose

# 3. Evaluate models
python3 training_pipeline/evaluator.py --compare gpt2_124M llmc_124M --report

# 4. Start inference server
python3 -m inference.model_server --verbose &
```

### Full Reconnaissance Workflow

```bash
# 1. Cloud recon with verbose mode
python3 run_cloud_recon.py --enhanced --apex target.com --verbose

# 2. Security recon with verbose mode
python3 run_recon.py --domain target.com --verbose --sync-bbrf

# 3. Benchmark AI analysis
python3 run_benchmark.py --domain target.com --verbose --advanced-report

# 4. Analyze with AI
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "target.com", "model": "gpt2_124M"}'
```

### Continuous Training Workflow

```bash
# 1. Start data collection (background)
python3 -m data_collector.main &

# 2. Run training scheduler with verbose mode
python3 training_pipeline/scheduler.py --verbose

# The scheduler will automatically:
# - Check for new reports every cycle
# - Trigger training when 1000+ new reports accumulate
# - Train all configured model sizes
# - Evaluate and compare models
# - Generate reports
```

---

## Quick Reference Card

### Core Commands
```bash
bash setup.sh                                    # Setup
python3 configure_apis.py --create-env          # Configure APIs
python3 training_pipeline/prepare_hackerone.py --tokenizer=both  # Prepare data
python3 training_pipeline/train_gpt2.py --model_size 124M  # Train GPT-2
python3 training_pipeline/train_llmc.py --model_size 124M --verbose  # Train llm.c
python3 training_pipeline/scheduler.py --verbose  # Continuous training
python3 -m inference.model_server --verbose     # Start server
python3 run_benchmark.py --domain example.com --verbose  # Benchmark
```

### Cloud Recon Commands
```bash
python3 run_cloud_recon.py --download --process  # Basic recon
python3 run_cloud_recon.py --enhanced --apex domain.com --verbose  # Enhanced recon
python3 run_cloud_recon.py --one-liners --apex domain.com  # Get commands
```

### Security Tools
```bash
httpx -u example.com -silent -json             # HTTP probe
katana -u example.com -silent -json             # Crawl
gau example.com --subs                          # Get URLs
nuclei -u example.com -silent -json             # Vuln scan
naabu -u example.com -silent -json             # Port scan
dnsx -u example.com -silent -json              # DNS resolve
amass enum -passive -d example.com -json        # Subdomain enum
subfinder -d example.com -silent               # Subdomain discovery
```

### API Endpoints
```bash
POST /generate                                  # Generate text
POST /analyze_domain                            # Analyze domain
GET /health                                     # Health check
```

---

## Notes

- All Python commands use `python3` (adjust to your system)
- Security tools must be installed separately and added to PATH
- API keys should be stored in `.env` file, never committed to git
- Results are saved in respective directories (benchmarking/results/, etc.)
- Always enable tools in `config.yaml` before use
- Verbose mode is recommended for development and debugging
- GPU training requires CUDA Toolkit (for llm.c and PyTorch models)
- PostgreSQL is required for data collection and full training pipeline

---

## System Requirements

### Minimum Requirements (llm.c CPU only)
- Python 3.10+
- clang compiler (for llm.c compilation)
- numpy, tiktoken (for data preparation)
- 8GB RAM
- 10GB disk space

### Recommended Requirements (Full System)
- Python 3.10+
- PostgreSQL 15+
- CUDA Toolkit 12.x (for GPU training)
- PyTorch 2.x
- 32GB RAM
- 100GB disk space
- GPU with 8GB+ VRAM (for training)

### Optional Enhancements
- cuDNN (for Flash Attention)
- NCCL (for multi-GPU training)
- MPI (for multi-node training)
- Redis (for caching)
- Docker (for containerization)

---

## Troubleshooting

### Common Issues

**Issue**: `nvcc not found`
**Solution**: Install CUDA Toolkit or use CPU version with `--use_gpu=False`

**Issue**: `pg_config not found`
**Solution**: Install PostgreSQL or use Docker

**Issue**: `ModuleNotFoundError for torch`
**Solution**: Install PyTorch: `pip install torch`

**Issue**: `llm.c training fails with "Failed to open file"`
**Solution**: Run `python llm.c/llm.c-master/train_gpt2.py` to download starter pack with weights

**Issue**: `OpenMP not found`
**Solution**: Install libomp (macOS: `brew install libomp`, Linux: `sudo apt install libomp-dev`)

**Issue**: Benchmark returns no results
**Solution**: Ensure models are trained and loaded, check API keys for external APIs

---

## Additional Documentation

- [README.md](README.md) - Project overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Setup instructions
- [SETUP_STATUS.md](SETUP_STATUS.md) - Current setup status
- [LLMC_INTEGRATION.md](LLMC_INTEGRATION.md) - llm.c integration guide
- [ENHANCED_CLOUD_RECON.md](ENHANCED_CLOUD_RECON.md) - Cloud recon features
- [COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md) - Original command reference
- [CONTINUOUS_LEARNING.md](CONTINUOUS_LEARNING.md) - Continuous learning system
- [EXTERNAL_APIS.md](EXTERNAL_APIS.md) - External API integration
- [SECURITY_TOOLS.md](SECURITY_TOOLS.md) - Security tools documentation
- [CLOUD_RECON.md](CLOUD_RECON.md) - Cloud recon documentation
- [GPT2_INTEGRATION.md](GPT2_INTEGRATION.md) - GPT-2 integration
- [HACKERONE_DATASET.md](HACKERONE_DATASET.md) - Dataset usage
- [TOOLS_SUMMARY.md](TOOLS_SUMMARY.md) - Tools summary
- [REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md) - Review checklist

---

For support and issues, see the project documentation or create an issue on GitHub.
