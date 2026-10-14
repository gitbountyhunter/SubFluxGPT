# SubFluxGPT - Complete Command Reference

This document provides a comprehensive list of all commands available in SubFluxGPT, including:
- Core SubFluxGPT commands
- Model training commands
- Inference server commands
- Security tool commands
- BBRF commands
- API commands

## Table of Contents
1. [Setup Commands](#setup-commands)
2. [Data Preparation Commands](#data-preparation-commands)
3. [Training Commands](#training-commands)
4. [Inference Commands](#inference-commands)
5. [Benchmarking Commands](#benchmarking-commands)
6. [Security Tool Commands](#security-tool-commands)
7. [BBRF Commands](#bbrf-commands)
8. [API Commands](#api-commands)
9. [Configuration Commands](#configuration-commands)

---

## Setup Commands

### Initial Setup
```bash
# Run the setup script (recommended)
bash setup.sh

# Manual installation
pip3 install -r requirements.txt

# Create directories
mkdir -p data/bugbounty_tokens data/hackerone_tokens data/hackerone_gpt2_tokens
mkdir -p models/checkpoints models/llama2c models/gpt2 models/nanogpt
mkdir -p benchmarking/results logs
```

### API Key Configuration
```bash
# Create .env template
python3 configure_apis.py --create-env

# List configured API keys
python3 configure_apis.py --list

# Edit .env file
nano .env
# or
vim .env
```

---

## Data Preparation Commands

### HackerOne Dataset Preparation
```bash
# Prepare data for llama2.c (SentencePiece tokenizer)
python3 training_pipeline/prepare_hackerone.py --tokenizer=llama2c

# Prepare data for GPT-2 (tiktoken tokenizer)
python3 training_pipeline/prepare_hackerone.py --tokenizer=gpt2

# Prepare data for both tokenizers
python3 training_pipeline/prepare_hackerone.py --tokenizer=both

# With custom vocabulary size (llama2.c only)
python3 training_pipeline/prepare_hackerone.py --tokenizer=llama2c --vocab_size 2048

# With custom train/val split
python3 training_pipeline/prepare_hackerone.py --tokenizer=both --train_split 0.8
```

### Database Data Preparation
```bash
# Prepare data from local database
python3 training_pipeline/prepare_bugbounty.py --vocab_size 4096

# With custom vocabulary size
python3 training_pipeline/prepare_bugbounty.py --vocab_size 2048
```

### HackerOne for nanoGPT
```bash
# Prepare data in nanoGPT format
python3 training_pipeline/prepare_hackerone_nanogpt.py
```

---

## Training Commands

### GPT-2 Training
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

### nanoGPT Training
```bash
# Train with HackerOne configuration
python3 config/finetune_hackerone.py

# Train with custom configuration
python3 nanoGPT/train.py config/train_hackerone.py
```

### Continuous Training Scheduler
```bash
# Run training scheduler (automatic training)
python3 training_pipeline/scheduler.py

# Run with custom config
python3 training_pipeline/scheduler.py --config custom_config.yaml
```

### llama2.c Training
```bash
# Train llama2.c 15M model
python3 llama2.c/train.py --batch_size 16 --learning_rate 5e-4 --max_iters 100000

# Train llama2.c 42M model
python3 llama2.c/train.py --dim 512 --n_layers 8 --n_heads 8 --batch_size 16

# Train llama2.c 110M model
python3 llama2.c/train.py --dim 768 --n_layers 12 --n_heads 12 --batch_size 16
```

---

## Inference Commands

### Start Inference Server
```bash
# Start server with default config
python3 -m inference.model_server

# Start with custom host/port
python3 -m inference.model_server --host 0.0.0.0 --port 8000

# Start with custom workers
python3 -m inference.model_server --workers 4
```

### Inference API Usage
```bash
# Generate text
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze example.com for subdomain takeover vulnerabilities",
    "model": "gpt2_124M",
    "max_new_tokens": 256,
    "temperature": 0.8,
    "top_p": 0.9
  }'

# Analyze domain
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "model": "gpt2_124M"
  }'

# Analyze domain with benchmark
curl -X POST http://localhost:8000/analyze_domain?run_benchmark=true \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "model": "gpt2_124M"
  }'

# Health check
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

# Run with custom output
python3 run_benchmark.py --domain example.com --output benchmarking/results/example.json

# Run with custom config
python3 run_benchmark.py --domain example.com --config custom_config.yaml
```

### Benchmark Analysis
```bash
# View latest results
cat benchmarking/results/latest.json

# Compare results over time
python3 -c "import json; data=json.load(open('benchmarking/results/latest.json')); print(json.dumps(data, indent=2))"
```

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

### MassDNS (High-Performance DNS)
```bash
# Resolve domains with massdns
echo -e "example.com A\ntest.com A" | massdns -r /etc/resolvers.txt -t A -o S -s 1000

# Resolve from file
massdns -r /etc/resolvers.txt -t A -o S -s 1000 < domains.txt
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

---

## BBRF Commands

### BBRF API (via Python)
```python
from recon_tools import BBRFClient

# Initialize client
bbrf = BBRFClient({
    'enabled': True,
    'api_endpoint': 'http://localhost:5000',
    'api_key': 'your-key',
    'workspace': 'subfluxgpt'
})

# Create program
bbrf.create_program('example.com')

# Add domain
bbrf.add_domain('example.com', 'example.com', source='subfluxgpt')

# Add subdomain
bbrf.add_subdomain('example.com', 'api.example.com', source='amass')

# Add URL
bbrf.add_url('example.com', 'https://api.example.com/', 200, source='httpx')

# Add vulnerability
bbrf.add_vulnerability('example.com', {
    'type': 'subdomain_takeover',
    'severity': 'high',
    'description': 'Subdomain takeover detected'
})

# Get domains
domains = bbrf.get_domains('example.com')

# Get subdomains
subdomains = bbrf.get_subdomains('example.com')
```

### BBRF CLI Commands
```bash
# Create new scope
bbrf new scope example.com

# Add domain to scope
bbrf scope add example.com

# List domains in scope
bbrf domains

# List subdomains in scope
bbrf subdomains

# List URLs in scope
bbrf urls

# Check if domain is in scope
bbrf inscope example.com
```

---

## API Commands

### External API Usage
```python
from external_apis import MultiAPIClient

# Initialize clients
config = {
    "openai": {"api_key": "sk-...", "model": "gpt-4-turbo"},
    "anthropic": {"api_key": "sk-ant-...", "model": "claude-3-opus-20240229"}
}

multi_client = MultiAPIClient(config)

# Generate with specific provider
response = await multi_client.generate("openai", "Analyze example.com")
print(response.content)

# Generate with all providers
responses = await multi_client.generate_all("Analyze example.com")
for resp in responses:
    print(f"{resp.provider}: {resp.content}")

# Cleanup
multi_client.close_all()
```

---

## Configuration Commands

### View Configuration
```bash
# View full config
cat config.yaml

# View specific section
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

# Update specific section
python3 -c "
import yaml
config = yaml.safe_load(open('config.yaml'))
config['training']['gpt2']['batch_size'] = 8
with open('config.yaml', 'w') as f:
    yaml.dump(config, f)
"
```

---

## Complete Workflow Example

### Full Reconnaissance Workflow
```bash
# 1. Prepare data
python3 training_pipeline/prepare_hackerone.py --tokenizer=both

# 2. Train model
python3 training_pipeline/train_gpt2.py --model_size 124M

# 3. Start inference server
python3 -m inference.model_server &

# 4. Enumerate subdomains with amass
amass enum -passive -d example.com -json > subdomains.json

# 5. Probe domains with httpx
cat subdomains.json | jq -r '.name' | httpx -silent -json -status-code

# 6. Get URLs from wayback
gau example.com --subs --threads 5 > urls.txt

# 7. Crawl URLs
katana -list urls.txt -silent -json -depth 2 > crawled_urls.txt

# 8. Deduplicate URLs
cat crawled_urls.txt | anew deduped_urls.txt

# 9. Scan for vulnerabilities
nuclei -list deduped_urls.txt -silent -json -severity high,critical

# 10. Run benchmark
python3 run_benchmark.py --domain example.com --compare

# 11. Analyze with AI
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "model": "gpt2_124M"}'

# 12. Or use integrated recon runner
python3 run_recon.py --domain example.com --sync-bbrf
```

---

## Quick Reference Card

### Core Commands
```bash
bash setup.sh                                    # Setup
python3 configure_apis.py --create-env          # Configure APIs
python3 training_pipeline/prepare_hackerone.py --tokenizer=both  # Prepare data
python3 training_pipeline/train_gpt2.py --model_size 124M  # Train
python3 -m inference.model_server               # Start server
python3 run_benchmark.py --domain example.com   # Benchmark
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
hakrawler -depth 3                              # Crawl
waybackurls example.com                         # Wayback URLs
subfinder -d example.com -silent               # Subdomain discovery
assetfinder --subs-only example.com            # Domain discovery
ffuf -u http://example.com/FUZZ -w wordlist   # Directory fuzzing
feroxbuster -u http://example.com -w wordlist # Directory discovery
arjun -u https://example.com/page              # Parameter discovery
subjs                                          # JS analysis
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

---

For more details, see:
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Setup instructions
- [EXTERNAL_APIS.md](EXTERNAL_APIS.md) - External API integration
- [GPT2_INTEGRATION.md](GPT2_INTEGRATION.md) - GPT-2 integration
- [HACKERONE_DATASET.md](HACKERONE_DATASET.md) - Dataset usage
