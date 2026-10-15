# BountyCatch Remix Integration Guide

Complete guide to integrating BountyCatch Remix with SubFluxGPT cloud reconnaissance.

## Overview

BountyCatch Remix is a bug bounty domain management tool for security researchers. SubFluxGPT now automatically exports cloud reconnaissance results to BountyCatch Remix for easy domain management.

---

## BountyCatch Remix Location

Your BountyCatch Remix is installed at:
```
~/bountycatchremix
```

---

## Cloud Recon with BountyCatch Export

### Automatic Export and Import

```bash
# Export and automatically import to BountyCatch Remix
subfluxgpt cloud --export --bountycatch-import --project example_recon

# Full workflow with BountyCatch
subfluxgpt cloud --full \
  --apex example.com \
  --project example_recon \
  --bountycatch-import \
  --verbose
```

### Export Only (Manual Import)

```bash
# Export to file
subfluxgpt cloud --export --project example_recon

# Then manually import to BountyCatch
cd ~/bountycatchremix
python3 bountycatch.py add -p example_recon -f /path/to/export.txt
```

### Using Python Script

```bash
# Export with automatic import
python3 run_cloud_recon.py \
  --export \
  --bountycatch-import \
  --project example_recon \
  --bountycatch-path ~/bountycatchremix

# Full workflow
python3 run_cloud_recon.py \
  --full \
  --apex example.com \
  --project example_recon \
  --bountycatch-import \
  --bountycatch-path ~/bountycatchremix \
  --verbose
```

---

## BountyCatch Integration in Bug Bounty Monitor

### Enable BountyCatch in Monitor

```bash
# Start monitoring with BountyCatch integration
subfluxgpt monitor-start \
  --interval 3600 \
  --organize-folders \
  --auto-recon \
  --enable-bountycatch \
  --bountycatch-path ~/bountycatchremix
```

### Monitor with All Integrations

```bash
# Start with BBRF and BountyCatch
subfluxgpt monitor-start \
  --interval 3600 \
  --organize-folders \
  --auto-recon \
  --enable-bbrf \
  --bbrf-api-key YOUR_API_KEY \
  --enable-bountycatch \
  --bountycatch-path ~/bountycatchremix \
  --output-dir targets/
```

This will:
- ✅ Monitor bug bounty platforms
- ✅ Create folders by company
- ✅ Automatically run recon
- ✅ Save to BBRF
- ✅ Export to BountyCatch Remix
- ✅ Feed to learning system

### Check Status

```bash
subfluxgpt monitor-status
```

**Output:**
```
Monitoring status: ACTIVE
BBRF integration: ENABLED
BountyCatch Remix integration: ENABLED
Folder organization: ENABLED
Auto recon: ENABLED
```

---

## BountyCatch Commands

### Basic BountyCatch Usage

```bash
cd ~/bountycatchremix

# Add domains from file
python3 bountycatch.py add -p example-project -f domains.txt

# Count domains in project
python3 bountycatch.py count -p example-project

# List all domains
python3 bountycatch.py print -p example-project

# Export domains
python3 bountycatch.py export -p example-project -f output.txt

# Export to JSON
python3 bountycatch.py export -p example-project -f output.json --format json

# Delete project
python3 bountycatch.py delete -p example-project
```

### Integration with SubFluxGPT

```bash
# Export from BountyCatch for SubFluxGPT
cd ~/bountycatchremix
python3 bountycatch.py export -p example-project -f domains.txt

# Use in SubFluxGPT
cd ~/Documents/Desktop/SubFluxGPT
subfinder -dL domains.txt -o new_subdomains.txt
```

---

## Complete Workflow Example

### 1. Cloud Recon with BountyCatch

```bash
# Run cloud recon and export to BountyCatch
subfluxgpt cloud --full \
  --apex example.com \
  --project example_recon \
  --bountycatch-import \
  --verbose
```

This will:
1. Download cloud provider data
2. Process SNI-IP ranges
3. Filter by apex domain
4. Export domains to file
5. Automatically import to BountyCatch Remix
6. Create project "example_recon"

### 2. Monitor with Automatic BountyCatch

```bash
# Start monitoring with BountyCatch
subfluxgpt monitor-start \
  --interval 3600 \
  --organize-folders \
  --auto-recon \
  --enable-bountycatch \
  --bountycatch-path ~/bountycatchremix
```

When a new program is detected:
1. Cloud recon runs automatically
2. Domains exported to BountyCatch
3. Project created by company name
4. Results saved to company folder
5. Data fed to learning system

### 3. Manual Workflow

```bash
# Step 1: Run cloud recon
subfluxgpt cloud --enhanced --apex example.com --verbose

# Step 2: Export to BountyCatch
subfluxgpt cloud --export --project example_recon

# Step 3: Import manually
cd ~/bountycatchremix
python3 bountycatch.py add -p example_recon -f /path/to/export.txt

# Step 4: Verify
python3 bountycatch.py count -p example_recon
python3 bountycatch.py print -p example_recon
```

---

## BountyCatch Project Naming

### Automatic Naming

When using the bug bounty monitor with `--organize-folders`:

- Company: `example_corp`
- Program: `example_corp_main_program`
- BountyCatch Project: `example_corp_main_program`

### Custom Naming

```bash
# Specify custom project name
subfluxgpt cloud --export --project my_custom_project --bountycatch-import

# In monitor, project name is based on company/program
# Company folder: targets/example_corp/example_corp_main_program/
# BountyCatch project: example_corp_main_program
```

---

## BountyCatch Features

### Domain Validation

BountyCatch automatically:
- Validates RFC-compliant domain names
- Detects and removes duplicates
- Skips invalid domains
- Provides statistics

### Project Organization

- Multiple projects for different targets
- Separate domain lists per project
- Easy export/import between projects

### Export Formats

**Text Format:**
```
api.example.com
example.com
subdomain.example.org
```

**JSON Format:**
```json
{
  "project": "example-project",
  "domain_count": 3,
  "exported_at": "2026-10-14T17:30:00",
  "domains": [
    "api.example.com",
    "example.com",
    "subdomain.example.org"
  ]
}
```

---

## Troubleshooting

### BountyCatch Not Found

**Error:**
```
✗ BountyCatch Remix not found at: ~/bountycatchremix
```

**Solution:**
```bash
# Verify BountyCatch path
ls -la ~/bountycatchremix

# Use correct path
subfluxgpt cloud --export --bountycatch-import --bountycatch-path /path/to/bountycatchremix
```

### Import Failed

**Error:**
```
✗ Import to BountyCatch Remix failed
```

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis if needed
brew services start redis  # macOS
sudo systemctl start redis  # Linux

# Try manual import
cd ~/bountycatchremix
python3 bountycatch.py add -p project -f file.txt
```

### Redis Connection Error

**Error:**
```
Error connecting to Redis
```

**Solution:**
```bash
# Install Redis
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux

# Verify
redis-cli ping
# Should return: PONG
```

---

## Summary

### Cloud Recon with BountyCatch ✅

```bash
# Automatic export and import
subfluxgpt cloud --export --bountycatch-import --project example_recon

# Full workflow
subfluxgpt cloud --full --apex example.com --project example_recon --bountycatch-import --verbose
```

### Monitor with BountyCatch ✅

```bash
subfluxgpt monitor-start \
  --interval 3600 \
  --organize-folders \
  --auto-recon \
  --enable-bountycatch \
  --bountycatch-path ~/bountycatchremix
```

### All Integrations ✅

```bash
subfluxgpt monitor-start \
  --interval 3600 \
  --organize-folders \
  --auto-recon \
  --enable-bbrf \
  --bbrf-api-key YOUR_API_KEY \
  --enable-bountycatch \
  --bountycatch-path ~/bountycatchremix \
  --output-dir targets/
```

---

## BountyCatch Benefits

✅ **Domain Management** - Organize domains by project
✅ **Validation** - Automatic domain validation
✅ **Deduplication** - Remove duplicate domains
✅ **Export Formats** - Text and JSON with metadata
✅ **Redis Storage** - Fast, persistent storage
✅ **Integration** - Easy integration with other tools

---

*Last Updated: 2026-10-14*
*BountyCatch Remix Path: ~/bountycatchremix*
