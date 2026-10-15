# Complete SubFluxGPT Command Reference

Every possible command iteration for SubFluxGPT with AI integration.

## Table of Contents
1. [Core SubFluxGPT Commands](#core-subfluxgpt-commands)
2. [AI-Integrated Tool Commands](#ai-integrated-tool-commands)
3. [Pipe Workflow Commands](#pipe-workflow-commands)
4. [Bug Bounty Platform Commands](#bug-bounty-platform-commands)
5. [Training and Fine-Tuning Commands](#training-and-fine-tuning-commands)
6. [Monitoring and Learning Commands](#monitoring-and-learning-commands)
7. [Advanced Custom Commands](#advanced-custom-commands)

---

## Core SubFluxGPT Commands

### Using the Alias (Recommended)

```bash
# Reload shell first
source ~/.zshrc

# Then use any command
subfluxgpt <command> [options]
```

### All Core Commands

#### 1. Training Commands

```bash
# Basic training (CPU)
subfluxgpt train --model_size 124M --use_gpu=False --verbose

# Training with GPU
subfluxgpt train --model_size 124M --use_gpu=True --verbose

# Train different sizes
subfluxgpt train --model_size 15M --use_gpu=False --verbose
subfluxgpt train --model_size 42M --use_gpu=False --verbose
subfluxgpt train --model_size 110M --use_gpu=False --verbose
subfluxgpt train --model_size 124M --use_gpu=False --verbose
subfluxgpt train --model_size 350M --use_gpu=False --verbose
subfluxgpt train --model_size 355M --use_gpu=False --verbose
subfluxgpt train --model_size 774M --use_gpu=False --verbose
subfluxgpt train --model_size 1558M --use_gpu=False --verbose

# Training with custom parameters
subfluxgpt train --model_size 124M --epochs 20 --batch_size 8 --learning_rate 1e-3 --verbose

# Train with llama2.c backend
python3 training_pipeline/train_llmc.py --model_size 124M --use_gpu=False --verbose

# Train with nanoGPT backend
python3 training_pipeline/train_gpt2.py --model_size 124M --verbose

# Train with llm.c backend (requires compiled binary)
cd llm.c/llm.c-master
./train_gpt2
```

#### 2. Benchmarking Commands

```bash
# Basic benchmark
subfluxgpt benchmark --domain example.com --verbose

# Advanced benchmark with statistical report
subfluxgpt benchmark --domain example.com --verbose --advanced-report

# Benchmark specific models
subfluxgpt benchmark --domain example.com --models "gpt2_124M,gpt2_355M" --verbose

# Benchmark specific backends
subfluxgpt benchmark --domain example.com --backends "llama2c,nanogpt" --verbose

# Benchmark all models
subfluxgpt benchmark --domain example.com --verbose --advanced-report

# Benchmark with custom iterations
python3 run_benchmark.py --domain example.com --iterations 100 --verbose
```

#### 3. Cloud Reconnaissance Commands

```bash
# Basic cloud recon
subfluxgpt cloud --download --process --verbose

# Enhanced cloud recon with apex domain
subfluxgpt cloud --enhanced --apex example.com --verbose

# Cloud recon with all features
subfluxgpt cloud --enhanced --apex example.com --port-scan --ssl-analysis --tech-fingerprint --verbose

# Get Jason Haddix style one-liners
subfluxgpt cloud --one-liners --apex example.com

# Cloud recon with custom output
subfluxgpt cloud --enhanced --apex example.com --output data/cloud_recon/example_com.json --verbose

# Cloud recon with AI analysis
python3 run_cloud_recon.py --enhanced --apex example.com --ai-analysis --verbose
```

#### 4. Security Reconnaissance Commands

```bash
# Basic recon
subfluxgpt recon --domain example.com --verbose

# Recon with subdomain discovery
subfluxgpt recon --domain example.com --subdomains --verbose

# Recon with port scanning
subfluxgpt recon --domain example.com --ports --verbose

# Recon with vulnerability scanning
subfluxgpt recon --domain example.com --vuln-scan --verbose

# Full recon (all features)
subfluxgpt recon --domain example.com --subdomains --ports --vuln-scan --tech-stack --verbose

# Recon with custom output
subfluxgpt recon --domain example.com --output data/recon/example_com.json --verbose

# Recon with AI analysis
python3 run_recon.py --domain example.com --ai-analysis --verbose
```

#### 5. Inference Server Commands

```bash
# Start inference server
subfluxgpt server --verbose

# Start with custom port
subfluxgpt server --port 8080 --verbose

# Start with custom model
subfluxgpt server --model models/gpt2_124M --verbose

# Start with multiple workers
subfluxgpt server --workers 4 --verbose

# Start with OpenAI-compatible API
python3 -m inference.model_server --host 0.0.0.0 --port 8000 --verbose

# Test inference server
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello SubFluxGPT", "model": "gpt2_124M"}'
```

#### 6. Scheduler Commands

```bash
# Start training scheduler
subfluxgpt scheduler --verbose

# Start with custom interval
subfluxgpt scheduler --interval 3600 --verbose

# Start scheduler with specific model
subfluxgpt scheduler --model_size 124M --verbose

# Start scheduler with GPU
subfluxgpt scheduler --use_gpu --verbose

# Manual trigger
python3 training_pipeline/scheduler.py --verbose --run-once
```

#### 7. Data Collection Commands

```bash
# Collect data from all platforms
subfluxgpt collect --all --verbose

# Collect from HackerOne only
subfluxgpt collect --platform hackerone --verbose

# Collect from Bugcrowd only
subfluxgpt collect --platform bugcrowd --verbose

# Collect with custom date range
subfluxgpt collect --start-date 2024-01-01 --end-date 2024-12-31 --verbose

# Collect and save to database
subfluxgpt collect --database data/bugbounty.db --verbose
```

#### 8. Monitoring Commands

```bash
# Start bug bounty platform monitor
subfluxgpt monitor --interval 3600

# Check platforms once
subfluxgpt monitor --check-once

# List new programs
subfluxgpt monitor --list-new

# List scope changes in last 24 hours
subfluxgpt monitor --list-changes 24

# List scope changes in last 7 days
subfluxgpt monitor --list-changes 168

# Monitor with custom interval
subfluxgpt monitor --interval 1800

# Monitor specific platform only
python3 bug_bounty_monitor.py --platform hackerone --interval 3600
```

#### 9. Fine-Tuning Commands

```bash
# Prepare dataset from learning data
subfluxgpt fine-tune --prepare-dataset

# Fine-tune with QLoRA
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --epochs 3

# Fine-tune with GPU
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --use-gpu

# Fine-tune with custom parameters
subfluxgpt fine-tune --finetune \
  --dataset data/datasets/bugbounty_finetune \
  --model-size 124M \
  --epochs 5 \
  --batch-size 8 \
  --learning-rate 1e-4

# Evaluate fine-tuned model
subfluxgpt fine-tune --evaluate models/finetuned/finetuned_124M --dataset data/datasets/test_dataset

# Fine-tune larger model
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 774M --use-gpu
```

#### 10. Learning Commands

```bash
# Start continuous learning
subfluxgpt learn --start

# Fetch reports once
subfluxgpt learn --fetch

# Process reports once
subfluxgpt learn --process

# Export training data
subfluxgpt learn --export

# Show learning statistics
subfluxgpt learn --stats

# Self-improving loop (manual)
python3 self_improving_llm.py --start
```

---

## AI-Integrated Tool Commands

### Important: AI Integration is AUTOMATIC

When you use the **Tool Wrapper**, AI analysis happens automatically. You don't need to manually integrate AI - it's built-in.

### Using AI-Integrated Tools

#### Method 1: Python Script (Recommended)

```bash
# All tools with AI analysis automatically enabled
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('httpx', ['-u', 'example.com'], enable_ai=True)
print(result['ai_analysis'])
"
```

#### Method 2: SubfluxGPT Alias (AI Automatic)

```bash
# AI is automatically integrated in these commands
subfluxgpt recon --domain example.com --verbose  # AI analysis included
subfluxgpt cloud --enhanced --apex example.com --verbose  # AI analysis included
```

### All AI-Integrated Tools

#### 1. HTTPX (HTTP Probing)

```bash
# Basic HTTPX with AI
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('httpx', ['-u', 'example.com', '-silent'], enable_ai=True)
print(result['ai_analysis'])
"

# HTTPX with JSON output and AI
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('httpx', ['-u', 'example.com', '-silent', '-json'], enable_ai=True)
print(result['ai_analysis'])
"

# HTTPX with tech stack detection (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('httpx', ['-u', 'example.com'], enable_ai=True)
# AI automatically detects: server, framework, CDN, language
print(result['ai_analysis'])
"
```

**AI Tasks for HTTPX:**
- `detect_tech_stack` - Identifies server, framework, CDN, language
- `find_vulnerabilities` - Analyzes HTTP responses for security issues

#### 2. Subfinder (Subdomain Discovery)

```bash
# Subfinder with AI classification
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('subfinder', ['-d', 'example.com', '-silent'], enable_ai=True)
print(result['ai_analysis'])
"

# Subfinder with takeover prediction (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('subfinder', ['-d', 'example.com'], enable_ai=True)
# AI automatically classifies: dev, prod, api, cdn subdomains
# AI predicts: subdomain takeover vulnerabilities
print(result['ai_analysis'])
"
```

**AI Tasks for Subfinder:**
- `classify_subdomains` - Classifies by type (dev, prod, api, cdn)
- `predict_takeover` - Predicts subdomain takeover vulnerabilities
- `analyze_patterns` - Analyzes subdomain naming patterns

#### 3. Katana (Web Crawling)

```bash
# Katana with AI endpoint extraction
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('katana', ['-u', 'https://example.com', '-silent'], enable_ai=True)
print(result['ai_analysis'])
"

# Katana with parameter analysis (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('katana', ['-u', 'https://example.com'], enable_ai=True)
# AI automatically extracts: endpoints, parameters, hidden pages
print(result['ai_analysis'])
"
```

**AI Tasks for Katana:**
- `extract_endpoints` - Extracts API endpoints and URLs
- `analyze_params` - Analyzes URL parameters for vulnerabilities
- `find_hidden_pages` - Identifies potentially hidden pages

#### 4. Nuclei (Vulnerability Scanning)

```bash
# Nuclei with AI prioritization
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('nuclei', ['-u', 'https://example.com', '-silent'], enable_ai=True)
print(result['ai_analysis'])
"

# Nuclei with chain analysis (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('nuclei', ['-u', 'https://example.com'], enable_ai=True)
# AI automatically prioritizes: critical, high, medium, low findings
# AI analyzes: attack chains, connected vulnerabilities
print(result['ai_analysis'])
"
```

**AI Tasks for Nuclei:**
- `prioritize_findings` - Prioritizes by severity
- `analyze_chain` - Analyzes attack chains
- `suggest_payloads` - Suggests custom payloads

#### 5. BBRF (Data Management)

```bash
# BBRF with AI correlation
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('bbrf', ['domain', 'add', 'example.com'], enable_ai=True)
print(result['ai_analysis'])
"

# BBRF with pattern detection (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('bbrf', ['domain', 'show', 'example.com'], enable_ai=True)
# AI automatically correlates: data, finds patterns, enriches intel
print(result['ai_analysis'])
"
```

**AI Tasks for BBRF:**
- `correlate_data` - Correlates related data points
- `find_patterns` - Finds patterns in data
- `enrich_intel` - Enriches with additional intelligence

#### 6. DNSX (DNS Resolution)

```bash
# DNSX with AI wildcard detection
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('dnsx', ['-d', 'example.com', '-silent'], enable_ai=True)
print(result['ai_analysis'])
"

# DNSX with suspicious analysis (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('dnsx', ['-d', 'example.com'], enable_ai=True)
# AI automatically detects: wildcard DNS, suspicious patterns
print(result['ai_analysis'])
"
```

**AI Tasks for DNSX:**
- `analyze_dns_records` - Analyzes DNS record patterns
- `detect_wildcards` - Detects wildcard DNS configurations
- `find_suspicious` - Identifies suspicious DNS patterns

#### 7. MassDNS (Mass DNS)

```bash
# MassDNS with AI pattern analysis
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('massdns', ['-r', 'resolvers.txt', 'domains.txt'], enable_ai=True)
print(result['ai_analysis'])
"

# MassDNS with zone detection (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('massdns', ['-r', 'resolvers.txt', 'domains.txt'], enable_ai=True)
# AI automatically analyzes: resolution patterns, DNS zones
print(result['ai_analysis'])
"
```

**AI Tasks for MassDNS:**
- `analyze_resolution_patterns` - Analyzes DNS resolution patterns
- `detect_dns_zones` - Detects DNS zone boundaries

#### 8. Naabu (Port Scanning)

```bash
# Naabu with AI service detection
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('naabu', ['-host', 'example.com', '-silent'], enable_ai=True)
print(result['ai_analysis'])
"

# Naabu with vulnerability prediction (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('naabu', ['-host', 'example.com'], enable_ai=True)
# AI automatically detects: services, predicts vulnerabilities
print(result['ai_analysis'])
"
```

**AI Tasks for Naabu:**
- `analyze_open_ports` - Analyzes open port patterns
- `detect_services` - Identifies services on ports
- `predict_vulnerabilities` - Predicts vulnerabilities based on services

#### 9. GAU (URL Archives)

```bash
# GAU with AI historical analysis
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('gau', ['example.com'], enable_ai=True)
print(result['ai_analysis'])
"

# GAU with parameter extraction (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('gau', ['example.com'], enable_ai=True)
# AI automatically analyzes: historical URLs, extracts parameters, detects changes
print(result['ai_analysis'])
"
```

**AI Tasks for GAU:**
- `analyze_historical_urls` - Analyzes historical URL patterns
- `find_parameters` - Extracts URL parameters
- `detect_changes` - Detects changes over time

#### 10. Waybackurls (Wayback Machine)

```bash
# Waybackurls with AI analysis
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('waybackurls', ['example.com'], enable_ai=True)
print(result['ai_analysis'])
"

# Waybackurls with live detection (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('waybackurls', ['example.com'], enable_ai=True)
# AI automatically analyzes: historical data, finds live endpoints, extracts params
print(result['ai_analysis'])
"
```

**AI Tasks for Waybackurls:**
- `analyze_historical` - Analyzes historical data
- `find_live` - Identifies still-live endpoints
- `extract_params` - Extracts parameters from URLs

#### 11. FFUF (Fuzzing)

```bash
# FFUF with AI anomaly detection
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('ffuf', ['-u', 'https://example.com/FUZZ', '-w', 'wordlist.txt'], enable_ai=True)
print(result['ai_analysis'])
"

# FFUF with wordlist suggestion (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('ffuf', ['-u', 'https://example.com/FUZZ', '-w', 'wordlist.txt'], enable_ai=True)
# AI automatically detects: anomalies, suggests wordlists
print(result['ai_analysis'])
"
```

**AI Tasks for FFUF:**
- `analyze_fuzz_results` - Analyzes fuzzing results for anomalies
- `detect_anomalies` - Detects response anomalies
- `suggest_wordlists` - Suggests optimal wordlists

#### 12. Hakrawler (Crawling)

```bash
# Hakrawler with AI JS extraction
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('hakrawler', ['-u', 'https://example.com'], enable_ai=True)
print(result['ai_analysis'])
"

# Hakrawler with endpoint discovery (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('hakrawler', ['-u', 'https://example.com'], enable_ai=True)
# AI automatically extracts: JS files, finds endpoints, analyzes crawl
print(result['ai_analysis'])
"
```

**AI Tasks for Hakrawler:**
- `extract_js` - Extracts JavaScript files
- `find_endpoints` - Finds API endpoints
- `analyze_crawl` - Analyzes crawl patterns

#### 13. Assetfinder (Asset Discovery)

```bash
# Assetfinder with AI classification
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('assetfinder', ['example.com'], enable_ai=True)
print(result['ai_analysis'])
"

# Assetfinder with scope analysis (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('assetfinder', ['example.com'], enable_ai=True)
# AI automatically classifies: assets, finds related assets, analyzes scope
print(result['ai_analysis'])
"
```

**AI Tasks for Assetfinder:**
- `classify_assets` - Classifies asset types
- `find_related` - Finds related assets
- `analyze_scope` - Analyzes asset scope

#### 14. Amass (Comprehensive Recon)

```bash
# Amass with AI attack surface analysis
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('amass', ['enum', '-d', 'example.com'], enable_ai=True)
print(result['ai_analysis'])
"

# Amass with correlation (AI task)
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('amass', ['enum', '-d', 'example.com'], enable_ai=True)
# AI automatically analyzes: attack surface, finds subdomains, correlates intel
print(result['ai_analysis'])
"
```

**AI Tasks for Amass:**
- `analyze_attack_surface` - Analyzes complete attack surface
- `find_subdomains` - Finds subdomains with AI prioritization
- `correlate_intel` - Correlates intelligence from multiple sources

---

## Pipe Workflow Commands

### Basic Pipe Workflows

```bash
# Subfinder -> HTTPX with AI
subfinder -d example.com -silent | \
  python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
import sys
wrapper = ToolWrapper()
for line in sys.stdin:
    result = wrapper.execute_tool('httpx', ['-silent', '-json'], enable_ai=True)
    print(result['ai_analysis'])
"

# HTTPX -> Nuclei with AI
httpx -u example.com -silent | \
  python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
import sys
wrapper = ToolWrapper()
for line in sys.stdin:
    result = wrapper.execute_tool('nuclei', ['-silent', '-json'], enable_ai=True)
    print(result['ai_analysis'])
"

# Full pipeline with AI at each step
subfinder -d example.com -silent | \
  httpx -silent -json | \
  jq -r '.url' | \
  nuclei -silent -json | \
  python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
import sys
wrapper = ToolWrapper()
for line in sys.stdin:
    print(json.dumps(json.loads(line), indent=2))
"
```

### Advanced Pipe Workflows

```python
# Python script for complex pipelines
from ai_integration.tool_wrapper import ToolWrapper

wrapper = ToolWrapper()

# Define pipeline
pipeline = [
    {'tool': 'subfinder', 'args': ['-d', 'example.com', '-silent']},
    {'tool': 'httpx', 'args': ['-silent', '-json']},
    {'tool': 'katana', 'args': ['-silent', '-json']},
    {'tool': 'nuclei', 'args': ['-silent', '-json']}
]

# Execute pipeline with AI at each step
results = wrapper.pipe_workflow(pipeline, enable_ai=True)

# View results
for step in results['steps']:
    print(f"{step['tool']}: {step.get('ai_analysis', {})}")
```

---

## Bug Bounty Platform Commands

### Enhanced Bug Bounty Monitor (with Folder Organization)

```bash
# Start monitor with automatic folder creation
python3 bug_bounty_monitor.py --interval 3600 --organize-folders

# Check once and organize by company
python3 bug_bounty_monitor.py --check-once --organize-folders

# Monitor specific platform and organize
python3 bug_bounty_monitor.py --platform hackerone --interval 3600 --organize-folders

# Custom output directory
python3 bug_bounty_monitor.py --interval 3600 --organize-folders --output-dir targets/
```

### Platform-Specific Commands

```bash
# HackerOne only
python3 bug_bounty_monitor.py --platform hackerone --interval 3600

# Bugcrowd only
python3 bug_bounty_monitor.py --platform bugcrowd --interval 3600

# YesWeHack only
python3 bug_bounty_monitor.py --platform yeswehack --interval 3600

# Intigriti only
python3 bug_bounty_monitor.py --platform intigriti --interval 3600

# Multiple platforms
python3 bug_bounty_monitor.py --platforms hackerone,bugcrowd --interval 3600
```

### Automatic Recon on New Programs

```bash
# Monitor and automatically run recon on new programs
python3 bug_bounty_monitor.py --interval 3600 --auto-recon --organize-folders

# Monitor with custom recon command
python3 bug_bounty_monitor.py --interval 3600 --auto-recon --recon-cmd "subfluxgpt recon --domain {domain} --verbose" --organize-folders
```

---

## Training and Fine-Tuning Commands

### All Training Options

```bash
# All model sizes with llama2.c
subfluxgpt train --model_size 15M --use_gpu=False --verbose
subfluxgpt train --model_size 42M --use_gpu=False --verbose
subfluxgpt train --model_size 110M --use_gpu=False --verbose

# All model sizes with nanoGPT
subfluxgpt train --model_size 124M --use_gpu=False --verbose
subfluxgpt train --model_size 355M --use_gpu=False --verbose
subfluxgpt train --model_size 774M --use_gpu=False --verbose
subfluxgpt train --model_size 1558M --use_gpu=False --verbose

# All model sizes with llm.c
python3 training_pipeline/train_llmc.py --model_size 124M --use_gpu=False --verbose
python3 training_pipeline/train_llmc.py --model_size 350M --use_gpu=False --verbose
python3 training_pipeline/train_llmc.py --model_size 774M --use_gpu=False --verbose
python3 training_pipeline/train_llmc.py --model_size 1558M --use_gpu=False --verbose

# With GPU
subfluxgpt train --model_size 124M --use_gpu=True --verbose
subfluxgpt train --model_size 774M --use_gpu=True --verbose
subfluxgpt train --model_size 1558M --use_gpu=True --verbose
```

### All Fine-Tuning Options

```bash
# Prepare dataset
subfluxgpt fine-tune --prepare-dataset

# Fine-tune all sizes
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --epochs 3
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 350M --epochs 3
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 774M --epochs 3
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 1558M --epochs 3

# With GPU
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --use-gpu --epochs 3

# Custom epochs
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --epochs 5
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --epochs 10

# Custom batch size
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --batch-size 2
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --batch-size 8

# Custom learning rate
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --learning-rate 1e-4
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune --model-size 124M --learning-rate 5e-5

# Evaluate all models
subfluxgpt fine-tune --evaluate models/finetuned/finetuned_124M --dataset data/datasets/test_dataset
subfluxgpt fine-tune --evaluate models/finetuned/finetuned_350M --dataset data/datasets/test_dataset
subfluxgpt fine-tune --evaluate models/finetuned/finetuned_774M --dataset data/datasets/test_dataset
subfluxgpt fine-tune --evaluate models/finetuned/finetuned_1558M --dataset data/datasets/test_dataset
```

---

## Monitoring and Learning Commands

### All Learning Options

```bash
# Start continuous learning
subfluxgpt learn --start

# Fetch from all platforms
subfluxgpt learn --fetch

# Process reports
subfluxgpt learn --process

# Export training data
subfluxgpt learn --export

# Show statistics
subfluxgpt learn --stats

# Manual learning cycle
python3 self_improving_llm.py --fetch
python3 self_improving_llm.py --process
python3 self_improving_llm.py --export
python3 self_improving_llm.py --stats
```

### All Monitoring Options

```bash
# Monitor with different intervals
subfluxgpt monitor --interval 600      # 10 minutes
subfluxgpt monitor --interval 1800     # 30 minutes
subfluxgpt monitor --interval 3600     # 1 hour
subfluxgpt monitor --interval 7200     # 2 hours
subfluxgpt monitor --interval 86400    # 24 hours

# List changes with different timeframes
subfluxgpt monitor --list-changes 1    # 1 hour
subfluxgpt monitor --list-changes 6    # 6 hours
subfluxgpt monitor --list-changes 12   # 12 hours
subfluxgpt monitor --list-changes 24   # 24 hours
subfluxgpt monitor --list-changes 48   # 48 hours
subfluxgpt monitor --list-changes 168  # 1 week
```

---

## Advanced Custom Commands

### Custom AI Analysis Script

```python
#!/usr/bin/env python3
# custom_ai_recon.py - Custom AI-powered reconnaissance

from ai_integration.tool_wrapper import ToolWrapper
from ai_integration.continuous_learner import ContinuousLearner
import json

class CustomAIRecon:
    def __init__(self):
        self.wrapper = ToolWrapper()
        self.learner = ContinuousLearner()

    def full_recon(self, domain):
        """Full AI-powered reconnaissance"""
        print(f"[*] Starting AI-powered recon on {domain}")

        # Subdomain discovery
        print("[*] Discovering subdomains...")
        subfinder_result = self.wrapper.execute_tool(
            'subfinder', ['-d', domain, '-silent'], enable_ai=True
        )
        self.learner.log_command('subfinder', ['-d', domain], 0, 5.0)

        # HTTP probing
        print("[*] Probing HTTP...")
        httpx_result = self.wrapper.execute_tool(
            'httpx', ['-silent', '-json'], enable_ai=True
        )

        # Vulnerability scanning
        print("[*] Scanning for vulnerabilities...")
        nuclei_result = self.wrapper.execute_tool(
            'nuclei', ['-silent', '-json'], enable_ai=True
        )

        # Port scanning
        print("[*] Scanning ports...")
        naabu_result = self.wrapper.execute_tool(
            'naabu', ['-silent', '-json'], enable_ai=True
        )

        # DNS analysis
        print("[*] Analyzing DNS...")
        dnsx_result = self.wrapper.execute_tool(
            'dnsx', ['-silent', '-json'], enable_ai=True
        )

        # Compile results
        results = {
            'domain': domain,
            'subdomains': subfinder_result['ai_analysis'],
            'http': httpx_result['ai_analysis'],
            'vulnerabilities': nuclei_result['ai_analysis'],
            'ports': naabu_result['ai_analysis'],
            'dns': dnsx_result['ai_analysis']
        }

        # Log workflow
        self.learner.log_workflow(
            ['subfinder', 'httpx', 'nuclei', 'naabu', 'dnsx'],
            success=True
        )

        return results

if __name__ == '__main__':
    import sys
    recon = CustomAIRecon()
    results = recon.full_recon(sys.argv[1])
    print(json.dumps(results, indent=2))
```

Usage:
```bash
python3 custom_ai_recon.py example.com
```

### Automated Bug Hunting Script

```python
#!/usr/bin/env python3
# automated_bug_hunter.py - Automated AI bug hunting

from ai_integration.tool_wrapper import ToolWrapper
from ai_integration.continuous_learner import ContinuousLearner
import json

class AutomatedBugHunter:
    def __init__(self):
        self.wrapper = ToolWrapper()
        self.learner = ContinuousLearner()

    def hunt(self, domain):
        """Automated bug hunting with AI"""
        print(f"[*] Hunting on {domain}")

        findings = []

        # Subdomain discovery
        subfinder_result = self.wrapper.execute_tool(
            'subfinder', ['-d', domain, '-silent'], enable_ai=True
        )

        # For each subdomain, run full recon
        # (In production, you'd iterate through subdomains)

        # HTTP probing
        httpx_result = self.wrapper.execute_tool(
            'httpx', ['-silent', '-json'], enable_ai=True
        )

        # Vulnerability scanning
        nuclei_result = self.wrapper.execute_tool(
            'nuclei', ['-silent', '-json'], enable_ai=True
        )

        # Analyze findings
        for finding in nuclei_result.get('ai_analysis', {}).get('findings', []):
            if finding['severity'] in ['critical', 'high']:
                print(f"[!] {finding['severity']}: {finding['finding']}")
                findings.append(finding)
                self.learner.log_finding(
                    'nuclei',
                    finding['finding'],
                    finding['severity'],
                    domain
                )

        return findings

if __name__ == '__main__':
    import sys
    hunter = AutomatedBugHunter()
    findings = hunter.hunt(sys.argv[1])
    print(json.dumps(findings, indent=2))
```

Usage:
```bash
python3 automated_bug_hunter.py example.com
```

---

## Summary

### AI Integration is AUTOMATIC

When you use:
- `subfluxgpt recon --domain example.com` → AI analysis included
- `subfluxgpt cloud --enhanced --apex example.com` → AI analysis included
- Tool wrapper in Python → AI analysis when `enable_ai=True`

### All Tools with AI

All 14+ tools have AI integration automatically:
- httpx, subfinder, katana, nuclei, bbrf, dnsx, massdns, naabu, gau, waybackurls, ffuf, hakrawler, assetfinder, amass

### Next: Enhanced Bug Bounty Monitor

I'll now enhance the bug bounty monitor to:
- Automatically create folders by company
- Organize scan results by target
- Feed apex domains and subdomains automatically

---

*Last Updated: 2026-10-14*
