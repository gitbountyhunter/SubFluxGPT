# SubFluxGPT - Complete Tools and Commands Summary

## ✅ Integration Status: COMPLETE

All 18 security tools have been successfully integrated into SubFluxGPT, plus the Cloud Recon module for SNI-IP range reconnaissance.

---

## Integrated Security Tools

### 1. **httpx** - HTTP Toolkit
- **Purpose**: Probe alive web servers, crawl for endpoints
- **Binary**: `httpx`
- **Config**: `security_tools.httpx`
- **Python Class**: `HTTPX`
- **Commands**:
  ```bash
  httpx -u example.com -silent -json -status-code
  httpx -u https://example.com -silent -json -scrape -depth 2
  ```

### 2. **katana** - Web Crawler
- **Purpose**: Discover endpoints by crawling
- **Binary**: `katana`
- **Config**: `security_tools.katana`
- **Python Class**: `Katana`
- **Commands**:
  ```bash
  katana -u https://example.com -silent -json -depth 2 -js-crawl
  katana -list urls.txt -silent -json -depth 3
  ```

### 3. **anew** - Deduplication Tool
- **Purpose**: Deduplicate domains, URLs, etc.
- **Binary**: `anew`
- **Config**: `security_tools.anew`
- **Python Class**: `Anew`
- **Commands**:
  ```bash
  echo -e "url1\nurl2\nurl1" | anew urls.txt
  cat urls.txt | anew deduped_urls.txt
  ```

### 4. **gau** - GetAllUrls
- **Purpose**: Get URLs from wayback machine
- **Binary**: `gau`
- **Config**: `security_tools.gau`
- **Python Class**: `GAU`
- **Commands**:
  ```bash
  gau example.com --subs --threads 5
  gau example.com --subs --blacklist "(css|js|png)"
  ```

### 5. **nuclei** - Vulnerability Scanner
- **Purpose**: Scan for vulnerabilities using templates
- **Binary**: `nuclei`
- **Config**: `security_tools.nuclei`
- **Python Class**: `Nuclei`
- **Commands**:
  ```bash
  nuclei -u https://example.com -silent -json -severity medium,high,critical
  nuclei -list targets.txt -silent -json -templates cves/
  ```

### 6. **naabu** - Port Scanner
- **Purpose**: Fast port scanning
- **Binary**: `naabu`
- **Config**: `security_tools.naabu`
- **Python Class**: `Naabu`
- **Commands**:
  ```bash
  echo "example.com" | naabu -silent -json -top-ports 1000
  echo "example.com" | naabu -silent -json -ports 80,443,8080
  ```

### 7. **dnsx** - DNS Toolkit
- **Purpose**: DNS resolution and wildcard detection
- **Binary**: `dnsx`
- **Config**: `security_tools.dnsx`
- **Python Class**: `DNSX`
- **Commands**:
  ```bash
  echo -e "example.com\ntest.com" | dnsx -silent -json -a -aaaa
  echo "example.com" | dnsx -silent -json -r 8.8.8.8
  ```

### 8. **massdns** - High-Performance DNS
- **Purpose**: Fast DNS resolution for large lists
- **Binary**: `massdns`
- **Config**: `security_tools.massdns`
- **Python Class**: `MassDNS`
- **Commands**:
  ```bash
  echo -e "example.com A\ntest.com A" | massdns -r /etc/resolvers.txt -t A -o S -s 1000
  massdns -r /etc/resolvers.txt -t A -o S -s 1000 < domains.txt
  ```

### 9. **amass** - Attack Surface Discovery
- **Purpose**: Subdomain enumeration and intelligence gathering
- **Binary**: `amass`
- **Config**: `security_tools.amass`
- **Python Class**: `Amass`
- **Commands**:
  ```bash
  amass enum -passive -d example.com -json
  amass enum -active -d example.com -json
  amass intel -d example.com -json
  ```

### 10. **hakrawler** - Web Crawler
- **Purpose**: Simple, fast web crawler for endpoints
- **Binary**: `hakrawler`
- **Config**: `security_tools.hakrawler`
- **Python Class**: `Hakrawler`
- **Commands**:
  ```bash
  echo "https://example.com" | hakrawler -depth 3
  echo "https://example.com" | hakrawler -depth 3 -subs
  cat urls.txt | hakrawler -depth 5
  ```

### 11. **waybackurls** - Wayback Machine URLs
- **Purpose**: Fetch URLs from wayback machine
- **Binary**: `waybackurls`
- **Config**: `security_tools.waybackurls`
- **Python Class**: `Waybackurls`
- **Commands**:
  ```bash
  waybackurls example.com
  waybackurls example.com -no-subs
  cat domains.txt | waybackurls
  ```

### 12. **subfinder** - Subdomain Discovery
- **Purpose**: Fast passive subdomain discovery
- **Binary**: `subfinder`
- **Config**: `security_tools.subfinder`
- **Python Class**: `Subfinder`
- **Commands**:
  ```bash
  subfinder -d example.com -silent
  subfinder -d example.com -all -silent
  subfinder -d example.com -json -silent
  ```

### 13. **assetfinder** - Domain Discovery
- **Purpose**: Find domains and subdomains
- **Binary**: `assetfinder`
- **Config**: `security_tools.assetfinder`
- **Python Class**: `Assetfinder`
- **Commands**:
  ```bash
  assetfinder --subs-only example.com
  assetfinder --subs-only example.com --ignore '*.test.com'
  cat domains.txt | assetfinder --subs-only
  ```

### 14. **crt.sh** - Certificate Transparency
- **Purpose**: Certificate transparency log search
- **Binary**: None (web service)
- **Config**: `security_tools.crtsh`
- **Python Class**: `Crtsh`
- **Commands**:
  ```bash
  curl -s "https://crt.sh/?q=%.example.com&output=json" | jq -r '.[].name_value'
  ```

### 15. **ffuf** - Web Fuzzer
- **Purpose**: Fast web fuzzer for directory discovery
- **Binary**: `ffuf`
- **Config**: `security_tools.ffuf`
- **Python Class**: `FFUF`
- **Commands**:
  ```bash
  ffuf -u http://example.com/FUZZ -w /usr/share/wordlists/dirb/common.txt
  ffuf -u http://example.com/FUZZ -w wordlist.txt -e php,html,js
  ffuf -u http://example.com/FUZZ -w wordlist.txt -mc 200,301,302
  ```

### 16. **feroxbuster** - Directory Discovery
- **Purpose**: Fast content discovery tool
- **Binary**: `feroxbuster`
- **Config**: `security_tools.feroxbuster`
- **Python Class**: `Feroxbuster`
- **Commands**:
  ```bash
  feroxbuster -u http://example.com -w /usr/share/wordlists/dirb/common.txt
  feroxbuster -u http://example.com -w wordlist.txt -x php,html,js
  feroxbuster -u http://example.com -w wordlist.txt -d 5
  ```

### 17. **arjun** - Parameter Discovery
- **Purpose**: Parameter discovery in web applications
- **Binary**: `arjun`
- **Config**: `security_tools.arjun`
- **Python Class**: `Arjun`
- **Commands**:
  ```bash
  arjun -u https://example.com/page?id=1
  arjun -u https://example.com/page -d "Authorization: Bearer token"
  ```

### 18. **subjs** - JavaScript Analysis
- **Purpose**: Find subdomains in JavaScript files
- **Binary**: `subjs`
- **Config**: `security_tools.subjs`
- **Python Class**: `Subjs`
- **Commands**:
  ```bash
  cat js_urls.txt | subjs
  echo -e "url1.js\nurl2.js" | subjs
  ```

---

## BBRF Integration

### BBRF Client
- **Purpose**: Manage and share reconnaissance data
- **Config**: `bbrf`
- **Python Classes**: `BBRFClient`, `BBRFCLI`
- **Features**:
  - Create programs/scopes
  - Add domains, subdomains, URLs
  - Add vulnerabilities
  - Query data

### BBRF Commands
```bash
bbrf new scope example.com
bbrf scope add example.com
bbrf domains
bbrf subdomains
bbrf urls
bbrf inscope example.com
```

---

## Core SubFluxGPT Commands

### Setup
```bash
bash setup.sh                                    # Initial setup
python3 configure_apis.py --create-env          # Configure API keys
```

### Data Preparation
```bash
python3 training_pipeline/prepare_hackerone.py --tokenizer=both
python3 training_pipeline/prepare_bugbounty.py --vocab_size 4096
```

### Training
```bash
python3 training_pipeline/train_gpt2.py --model_size 124M
python3 training_pipeline/scheduler.py
```

### Inference
```bash
python3 -m inference.model_server
curl -X POST http://localhost:8000/analyze_domain -H "Content-Type: application/json" -d '{"domain": "example.com"}'
```

### Benchmarking
```bash
python3 run_benchmark.py --domain example.com --compare
```

### Reconnaissance
```bash
python3 run_recon.py --domain example.com
python3 run_recon.py --domain example.com --sync-bbrf
python3 run_recon.py --domain example.com --tools httpx gau nuclei
```

---

## Complete Workflow Commands

### Quick Start Workflow
```bash
# 1. Setup
bash setup.sh

# 2. Configure APIs
python3 configure_apis.py --create-env
# Edit .env with your keys

# 3. Prepare data
python3 training_pipeline/prepare_hackerone.py --tokenizer=both

# 4. Train model
python3 training_pipeline/train_gpt2.py --model_size 124M

# 5. Start server
python3 -m inference.model_server &

# 6. Run reconnaissance
python3 run_recon.py --domain example.com --sync-bbrf

# 7. Run benchmark
python3 run_benchmark.py --domain example.com --compare
```

### Full Security Reconnaissance Workflow
```bash
# 1. Subdomain enumeration
amass enum -passive -d example.com -json > subdomains.json

# 2. DNS resolution
cat subdomains.json | jq -r '.name' | dnsx -silent -json -a -aaaa

# 3. HTTP probing
cat subdomains.json | jq -r '.name' | httpx -silent -json -status-code

# 4. URL discovery
gau example.com --subs --threads 5 > urls.txt

# 5. Crawling
katana -list urls.txt -silent -json -depth 2 > crawled_urls.txt

# 6. Deduplication
cat crawled_urls.txt | anew deduped_urls.txt

# 7. Port scanning
cat subdomains.json | jq -r '.name' | naabu -silent -json -top-ports 1000

# 8. Vulnerability scanning
nuclei -list deduped_urls.txt -silent -json -severity high,critical

# 9. AI analysis
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "model": "gpt2_124M"}'

# 10. Benchmark
python3 run_benchmark.py --domain example.com --compare

# 11. Sync to BBRF
python3 run_recon.py --domain example.com --sync-bbrf
```

---

## Python API Usage

### Security Tools
```python
from recon_tools import SecurityToolManager

manager = SecurityToolManager(config)
results = manager.run_reconnaissance('example.com')
```

### Individual Tools
```python
from recon_tools import HTTPX, Katana, Nuclei, Amass

httpx = HTTPX({'enabled': True, 'binary_path': 'httpx'})
result = httpx.probe(['example.com'])

amass = Amass({'enabled': True, 'binary_path': 'amass'})
result = amass.enum('example.com')
```

### BBRF
```python
from recon_tools import BBRFClient

bbrf = BBRFClient({'enabled': True, 'api_key': 'your-key'})
bbrf.create_program('example.com')
bbrf.add_domain('example.com', 'example.com')
```

### External APIs
```python
from external_apis import MultiAPIClient

multi_client = MultiAPIClient(config)
response = await multi_client.generate('openai', 'Analyze example.com')
```

---

## Configuration Files

### config.yaml Sections
- `database` - Database configuration
- `external_apis` - OpenAI, Anthropic, Cohere, etc.
- `local_models` - llama2.c, GPT-2 models
- `security_tools` - httpx, katana, nuclei, amass, etc.
- `bbrf` - BBRF integration
- `training` - Model training settings
- `inference` - Server settings
- `benchmarking` - Benchmark settings

### .env File
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...
BBRF_API_KEY=...
```

---

## Documentation Files

1. **SETUP_GUIDE.md** - Quick start guide
2. **COMMANDS_REFERENCE.md** - Complete command reference
3. **SECURITY_TOOLS.md** - Security tools installation and usage
4. **EXTERNAL_APIS.md** - External API integration
5. **GPT2_INTEGRATION.md** - GPT-2 integration details
6. **HACKERONE_DATASET.md** - Dataset documentation
7. **REVIEW_CHECKLIST.md** - Code review and fixes
8. **TOOLS_SUMMARY.md** - This file

---

## Model Architectures

### llama2.c
- 15M, 42M, 110M models
- SentencePiece tokenizer
- Custom vocabulary sizes

### nanoGPT
- Custom sizes
- GPT-2 compatible
- tiktoken tokenizer

### GPT-2 (HuggingFace)
- 124M (gpt2)
- 355M (gpt2-medium)
- 774M (gpt2-large)
- 1558M (gpt2-xl)

---

## Key Scripts

- `setup.sh` - One-time setup
- `configure_apis.py` - API configuration
- `run_benchmark.py` - Benchmark runner
- `run_recon.py` - Reconnaissance runner
- `training_pipeline/train_gpt2.py` - GPT-2 training
- `training_pipeline/scheduler.py` - Continuous training
- `training_pipeline/prepare_hackerone.py` - Data preparation

---

## All Commands Quick Reference

### Core
```bash
bash setup.sh
python3 configure_apis.py --create-env
python3 configure_apis.py --list
python3 training_pipeline/prepare_hackerone.py --tokenizer=both
python3 training_pipeline/train_gpt2.py --model_size 124M
python3 -m inference.model_server
python3 run_benchmark.py --domain example.com --compare
python3 run_recon.py --domain example.com --sync-bbrf
```

### Security Tools
```bash
httpx -u example.com -silent -json
katana -u example.com -silent -json
gau example.com --subs
nuclei -u example.com -silent -json
naabu -u example.com -silent -json
dnsx -u example.com -silent -json
massdns -r /etc/resolvers.txt -t A -o S
amass enum -passive -d example.com -json
```

### BBRF
```bash
bbrf new scope example.com
bbrf scope add example.com
bbrf domains
bbrf subdomains
bbrf urls
```

---

## Status: ✅ COMPLETE

All tools integrated:
- ✅ 18 Security tools (httpx, katana, anew, gau, nuclei, naabu, dnsx, massdns, amass, hakrawler, waybackurls, subfinder, assetfinder, crt.sh, ffuf, feroxbuster, arjun, subjs)
- ✅ BBRF integration
- ✅ 30+ External API providers
- ✅ 3 Model architectures (llama2.c, nanoGPT, GPT-2)
- ✅ Benchmarking system
- ✅ HackerOne dataset integration
- ✅ Complete documentation
- ✅ All configuration files
- ✅ All wrapper scripts

**SubFluxGPT is fully ready for production use!** 🚀
