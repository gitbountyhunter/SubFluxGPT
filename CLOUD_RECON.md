# Cloud Recon Module - SNI-IP Range Reconnaissance

## Overview

Cloud Recon is a world-class automated SNI-IP range reconnaissance module for SubFluxGPT. Based on Jason Haddix's proven workflow with AI-powered enhancements for bug bounty hunters.

### Features

✅ **Automated Download**: Downloads SNI-IP range data from 5 cloud providers
✅ **Multi-Provider Support**: Amazon, DigitalOcean, Google, Microsoft, Oracle
✅ **Jason Haddix Workflow**: Exact one-liner commands for manual processing
✅ **AI Analysis**: Intelligent domain analysis and risk assessment
✅ **Wildcard Detection**: Separates and removes wildcard domains
✅ **Apex Domain Extraction**: Identifies and groups by apex domains
✅ **BountyCatch Integration**: Direct export to BountyCatch Remix
✅ **High-Value Target Identification**: AI-powered target prioritization
✅ **Pattern Analysis**: Discovers interesting domain patterns
✅ **Risk Assessment**: Evaluates attack surface risk level

### Cloud Providers

1. **Amazon** - AWS SNI-IP ranges
2. **DigitalOcean** - DO cloud SNI data
3. **Google** - GCP SNI-IP ranges
4. **Microsoft** - Azure SNI data
5. **Oracle** - Oracle Cloud SNI ranges

---

## Installation

### Prerequisites

```bash
# Python dependencies
pip install requests

# Redis (for BountyCatch Remix)
brew install redis  # macOS
# or
sudo apt install redis-server  # Linux
```

### Setup

```bash
# Cloud Recon is included in SubFluxGPT
cd /Users/beanman/Documents/Desktop/SubFluxGPT

# Output directory will be created automatically
./cloud_recon_data/
```

---

## Jason Haddix One-Liner Commands

These are the exact one-liner commands used for manual SNI-IP range processing.

### Command 1: Extract Wildcard Domains

**Purpose**: Extract all wildcard domains from SNI data for a specific apex domain.

```bash
cd cloud_recon_data/raw/amazon && cat *.txt | grep -F "dell.com" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep "*" | sort -u
```

**Breakdown**:
- `cat *.txt` - Concatenate all downloaded files
- `grep -F "dell.com"` - Filter for lines containing the apex domain
- `grep -oP "(?<=\[).*(?=\])"` - Extract content between square brackets
- `tr ' ' '\n'` - Replace spaces with newlines (one domain per line)
- `grep "*"` - Filter for wildcard domains (containing asterisk)
- `sort -u` - Sort and remove duplicates

### Command 2: Extract Clean Domains (No Wildcards)

**Purpose**: Extract clean domains without wildcards.

```bash
cd cloud_recon_data/raw/amazon && cat *.txt | grep -F "dell.com" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep -v "*" | sort -u > cloud_recon_data/processed/amazon_clean.txt
```

**Breakdown**:
- Same as above until `grep -v "*"` - Invert wildcard filter (exclude wildcards)
- `> cloud_recon_data/processed/amazon_clean.txt` - Save to file

### Command 3: Extract Apex Domains

**Purpose**: Extract apex domains from clean domain list.

```bash
cat cloud_recon_data/processed/amazon_clean.txt | awk -F. '{print $(NF-1)"."$NF}' | sort -u
```

**Breakdown**:
- `awk -F. '{print $(NF-1)"."$NF}'` - Extract last two parts (domain + TLD)
- `sort -u` - Sort and deduplicate

### Command 4: Combine All Providers

**Purpose**: Combine processed data from all cloud providers.

```bash
cat cloud_recon_data/processed/*.txt | sort -u > cloud_recon_data/processed/all_combined.txt
```

### Command 5: Import to BountyCatch Remix

**Purpose**: Import processed domains into BountyCatch Remix.

```bash
python3 bountycatch.py add -p dell_cloud -f cloud_recon_data/processed/amazon_clean.txt
```

---

## Automated Usage

### Quick Start

```bash
# Download data from all providers
python3 run_cloud_recon.py --download

# Process all providers
python3 run_cloud_recon.py --process

# Export for BountyCatch
python3 run_cloud_recon.py --export --project dell_recon
```

### Full Workflow

```bash
# Run complete workflow with AI analysis
python3 run_cloud_recon.py --full --apex dell.com --project dell_recon --ai
```

### Filter by Apex Domain

```bash
# Process only domains related to dell.com
python3 run_cloud_recon.py --full --apex dell.com --project dell_recon
```

### Specific Provider

```bash
# Process only Amazon data
python3 run_cloud_recon.py --full --provider amazon --apex dell.com
```

### Get One-Liner Commands

```bash
# Show one-liner commands for manual processing
python3 run_cloud_recon.py --one-liners --apex dell.com

# For specific provider
python3 run_cloud_recon.py --one-liners --apex dell.com --provider amazon
```

---

## Python API Usage

### Basic Usage

```python
from cloud_recon import CloudReconManager

# Initialize
manager = CloudReconManager({'output_dir': './cloud_recon_data'})

# Download all provider data
download_results = manager.cloud_recon.download_all_providers()

# Process all providers
process_results = manager.cloud_recon.process_all_providers(
    apex_domain='dell.com',
    keep_wildcards=True
)

# Export for BountyCatch
export_path = manager.cloud_recon.export_for_bountycatch('dell_recon')
```

### Full Workflow with AI

```python
from cloud_recon import CloudReconManager

manager = CloudReconManager()

results = manager.run_full_workflow(
    apex_domain='dell.com',
    project_name='dell_recon',
    ai_analysis=True
)

# Access AI analysis
ai_results = results['steps']['ai_analysis']
print(f"Risk Level: {ai_results['risk_assessment']['level']}")
print(f"High-Value Targets: {len(ai_results['high_value_targets'])}")
```

### Custom Processing

```python
from cloud_recon import CloudRecon

cloud_recon = CloudRecon('./cloud_recon_data')

# Download specific provider
cloud_recon.download_provider_data('amazon')

# Process with custom apex domain
results = cloud_recon.process_provider_data(
    'amazon',
    apex_domain='dell.com',
    keep_wildcards=False
)

# Access results
print(f"Domains: {len(results['domains'])}")
print(f"Wildcards: {len(results['wildcards'])}")
print(f"Apex: {len(results['apex_domains'])}")
```

---

## AI Analysis Features

### High-Value Target Identification

The AI analyzer identifies high-value targets based on keyword matching:

- **Admin**: admin, console, dashboard, panel, control
- **API**: api, graphql, rest, soap, endpoint
- **Auth**: auth, login, oauth, sso, identity
- **Data**: db, database, storage, bucket, cache
- **Payment**: payment, billing, account, user

### Sensitive Domain Detection

Identifies potentially sensitive domains containing:

- **Keys**: key, secret, token, password, credential
- **Internal**: internal, private, intranet, dev, staging
- **Admin**: admin, console, dashboard
- **API**: api, graphql, rest

### Risk Assessment

Evaluates attack surface risk based on:

- Number of domains
- Number of wildcards
- Sensitive domain count
- High-value target count

**Risk Levels**: LOW, MEDIUM, HIGH, CRITICAL

### Pattern Analysis

Analyzes domain patterns:

- Subdomain depth distribution
- Common prefixes (api, admin, etc.)
- Common suffixes
- TLD distribution
- Domain length distribution

### Recommendations

AI generates actionable recommendations:

- Prioritize high-value targets
- Carefully test sensitive domains
- Allocate resources based on risk level
- Suggest specific testing strategies

---

## Output Structure

```
cloud_recon_data/
├── raw/                          # Downloaded raw data
│   ├── amazon/
│   │   ├── file1.txt
│   │   ├── file2.txt
│   │   └── ...
│   ├── digitalocean/
│   ├── google/
│   ├── microsoft/
│   └── oracle/
├── processed/                    # Processed clean domains
│   ├── amazon_domains.txt
│   ├── digitalocean_domains.txt
│   ├── google_domains.txt
│   ├── microsoft_domains.txt
│   ├── oracle_domains.txt
│   └── all_providers_domains.txt
├── wildcards/                    # Wildcard domains
│   ├── amazon_wildcards.txt
│   ├── digitalocean_wildcards.txt
│   └── all_providers_wildcards.txt
├── apex/                        # Apex domains
│   ├── amazon_apex.txt
│   ├── digitalocean_apex.txt
│   └── all_providers_apex.txt
├── bountycatch/                  # BountyCatch exports
│   └── project_name.txt
└── workflow_results.json        # Full workflow results
```

---

## Integration with BountyCatch Remix

### Automatic Export

```bash
# Export and import in one command
python3 run_cloud_recon.py --full --export --project dell_recon

# Then import to BountyCatch
python3 bountycatch.py add -p dell_recon -f cloud_recon_data/bountycatch/dell_recon.txt
```

### Manual Export

```python
from cloud_recon import CloudRecon

cloud_recon = CloudRecon()
export_path = cloud_recon.export_for_bountycatch('dell_recon')
print(f"Exported to: {export_path}")
```

### BountyCatch Remix Commands

```bash
# Add domains
python3 bountycatch.py add -p dell_recon -f cloud_recon_data/bountycatch/dell_recon.txt

# Count domains
python3 bountycatch.py count -p dell_recon

# List domains
python3 bountycatch.py print -p dell_recon

# Export to JSON
python3 bountycatch.py export -p dell_recon -f dell_recon.json --format json
```

---

## Advanced Features

### Tiered Domain Extraction

Extract domains by subdomain depth:

```python
from cloud_recon.parser import SNIParser

parser = SNIParser()
domains = parser.parse_file('cloud_recon_data/raw/amazon/file.txt', 'amazon')
tiers = parser.extract_tiered_domains(domains, max_depth=3)

# Access
print(f"Apex: {tiers['apex']}")
print(f"Tier 1: {tiers['tier1']}")
print(f"Tier 2: {tiers['tier2']}")
```

### Pattern Discovery

Discover interesting patterns in domains:

```python
from cloud_recon.parser import SNIParser

parser = SNIParser()
domains = parser.parse_file('cloud_recon_data/raw/amazon/file.txt', 'amazon')
patterns = parser.find_interesting_patterns(domains)

# Access
print(f"Dev domains: {patterns['dev']}")
print(f"API domains: {patterns['api']}")
print(f"Admin domains: {patterns['admin']}")
```

### Optimal Test Order

AI suggests optimal testing order:

```python
from cloud_recon.ai_analyzer import CloudAIAnalyzer

analyzer = CloudAIAnalyzer()
test_order = analyzer.suggest_test_order(domains)

# Test in this order for maximum impact
for domain in test_order[:100]:
    # Run your tests
    pass
```

---

## Performance Optimization

### Parallel Processing

Cloud Recon uses ThreadPoolExecutor for:

- Parallel downloads from all 5 providers
- Parallel processing of provider data
- Concurrent domain analysis

### Caching

The parser maintains caches for:

- Domain information
- Wildcard patterns
- Apex domain mappings

### Memory Efficiency

- Processes files line-by-line
- Uses generators where possible
- Efficient deduplication with sets

---

## Troubleshooting

### Download Fails

```bash
# Check internet connection
curl -I https://kaeferjaeger.gay

# Try manual download
wget https://kaeferjaeger.gay/?dir=sni-ip-ranges/amazon
```

### No Domains Found

```bash
# Check raw data
ls -la cloud_recon_data/raw/amazon/

# Verify file content
head cloud_recon_data/raw/amazon/*.txt

# Try different apex domain
python3 run_cloud_recon.py --process --apex example.com
```

### BountyCatch Import Fails

```bash
# Check Redis is running
redis-cli ping

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux

# Verify export file
cat cloud_recon_data/bountycatch/project_name.txt
```

---

## Complete Workflow Example

### Target: Dell Corporation

```bash
# Step 1: Download all cloud provider data
python3 run_cloud_recon.py --download

# Step 2: Process for dell.com with AI analysis
python3 run_cloud_recon.py --full --apex dell.com --project dell_recon --ai

# Step 3: Review AI analysis
cat cloud_recon_data/workflow_results.json | jq '.steps.ai_analysis'

# Step 4: Import to BountyCatch
python3 bountycatch.py add -p dell_recon -f cloud_recon_data/bountycatch/dell_recon.txt

# Step 5: Start subdomain enumeration
python3 bountycatch.py export -p dell_recon -f dell_subdomains.txt
subfinder -dL dell_subdomains.txt -o new_subdomains.txt

# Step 6: Import discovered subdomains
python3 bountycatch.py add -p dell_recon -f new_subdomains.txt

# Step 7: Run reconnaissance
python3 run_recon.py --domain dell.com --sync-bbrf
```

---

## One-Liner Command Reference

### Quick Reference Card

```bash
# Extract wildcards
cd cloud_recon_data/raw/<provider> && cat *.txt | grep -F "<apex>" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep "*" | sort -u

# Extract clean domains
cd cloud_recon_data/raw/<provider> && cat *.txt | grep -F "<apex>" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep -v "*" | sort -u > output.txt

# Extract apex domains
cat output.txt | awk -F. '{print $(NF-1)"."$NF}' | sort -u

# Combine all providers
cat cloud_recon_data/processed/*.txt | sort -u > combined.txt

# Import to BountyCatch
python3 bountycatch.py add -p <project> -f output.txt
```

### Provider-Specific Commands

```bash
# Amazon
cd cloud_recon_data/raw/amazon && cat *.txt | grep -F "dell.com" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep -v "*" | sort -u

# DigitalOcean
cd cloud_recon_data/raw/digitalocean && cat *.txt | grep -F "dell.com" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep -v "*" | sort -u

# Google
cd cloud_recon_data/raw/google && cat *.txt | grep -F "dell.com" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep -v "*" | sort -u

# Microsoft
cd cloud_recon_data/raw/microsoft && cat *.txt | grep -F "dell.com" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep -v "*" | sort -u

# Oracle
cd cloud_recon_data/raw/oracle && cat *.txt | grep -F "dell.com" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep -v "*" | sort -u
```

---

## Best Practices

1. **Always filter by apex domain** - Processing all domains at once can be overwhelming
2. **Keep wildcards for separate analysis** - Wildcards can reveal patterns
3. **Use AI analysis for prioritization** - High-value targets first
4. **Import to BountyCatch Remix** - Better domain management
5. **Combine with other tools** - Use with subfinder, httpx, nuclei
6. **Regular updates** - Cloud IP ranges change frequently
7. **Backup processed data** - Keep historical comparisons
8. **Review AI recommendations** - They're based on real bug bounty patterns

---

## Advanced Tips

### Custom Pattern Matching

```python
import re

# Add custom patterns to parser
custom_pattern = re.compile(r'custom-regex-here')
```

### Multi-Apex Processing

```bash
# Process multiple apex domains
for apex in dell.com hp.com apple.com; do
    python3 run_cloud_recon.py --full --apex $apex --project ${apex//./_}_recon
done
```

### Differential Analysis

```bash
# Compare today's results with yesterday
diff cloud_recon_data/processed/all_providers_domains.txt \
     cloud_recon_data/backup/all_providers_domains.txt
```

---

## Credits

- **Jason Haddix** - Original workflow and one-liner methodology
- **Kaeferjaeger** - SNI-IP range data source (https://kaeferjaeger.gay)
- **BountyCatch Remix** - Domain management tool

---

## Status: ✅ World-Class

Cloud Recon is a production-ready, world-class module for SNI-IP range reconnaissance with:
- ✅ 5 Cloud provider support
- ✅ Jason Haddix workflow implementation
- ✅ AI-powered analysis
- ✅ BountyCatch Remix integration
- ✅ Complete one-liner command reference
- ✅ Advanced pattern detection
- ✅ Risk assessment
- ✅ High-value target identification

**Ready for bug bounty reconnaissance!** 🚀
