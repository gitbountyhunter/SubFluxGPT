# BBRF Integration Guide

Complete guide to BBRF (Bug Bounty Reconnaissance Framework) integration in SubFluxGPT.

## Overview

BBRF is a framework for managing and sharing reconnaissance data. SubFluxGPT integrates BBRF to:
- Automatically save discovered domains and subdomains
- Track scope changes
- Share reconnaissance data across platforms
- Maintain persistent data storage

---

## BBRF Integration Status

✅ **BBRF is Already Integrated**

SubFluxGPT includes a complete BBRF client (`recon_tools/bbrf_client.py`) with:
- API client for BBRF server
- CLI wrapper for BBRF commands
- Automatic data synchronization
- Program, domain, subdomain, URL, and vulnerability management

---

## Monitoring with BBRF

### Enable BBRF in Bug Bounty Monitor

```bash
# Start monitoring with BBRF enabled
python3 bug_bounty_monitor.py \
  --interval 3600 \
  --organize-folders \
  --auto-recon \
  --enable-bbrf \
  --bbrf-endpoint http://localhost:5000 \
  --bbrf-api-key YOUR_API_KEY \
  --bbrf-workspace subfluxgpt
```

### Using SubFluxGPT Alias

```bash
# Start monitoring with BBRF
subfluxgpt monitor --start \
  --interval 3600 \
  --organize-folders \
  --auto-recon \
  --enable-bbrf \
  --bbrf-endpoint http://localhost:5000 \
  --bbrf-api-key YOUR_API_KEY
```

### BBRF Configuration Options

```bash
--enable-bbrf              # Enable BBRF integration
--bbrf-endpoint <url>      # BBRF API endpoint (default: http://localhost:5000)
--bbrf-api-key <key>       # BBRF API key (or set BBRF_API_KEY env var)
--bbrf-workspace <name>    # BBRF workspace name (default: subfluxgpt)
```

---

## On/Off Switch for Monitoring

### Using Command-Line Flags

```bash
# Turn monitoring ON
python3 bug_bounty_monitor.py --start

# Turn monitoring OFF
python3 bug_bounty_monitor.py --stop

# Check monitoring status
python3 bug_bounty_monitor.py --status
```

### Using SubFluxGPT Alias

```bash
# Turn monitoring ON
subfluxgpt monitor-start --interval 3600 --organize-folders

# Turn monitoring OFF
subfluxgpt monitor-stop

# Check monitoring status
subfluxgpt monitor-status
```

### Monitoring Status Output

```bash
$ subfluxgpt monitor-status

Monitoring status: ACTIVE
BBRF integration: ENABLED
Folder organization: ENABLED
Auto recon: ENABLED
```

---

## BBRF Features

### Automatic Data Saving

When BBRF is enabled, the monitor automatically saves:

1. **Programs**
   - Company name
   - Program name
   - Platform (HackerOne, Bugcrowd, etc.)
   - Program URL
   - Metadata

2. **Apex Domains**
   - All apex domains in scope
   - Source: bug_bounty_monitor

3. **Subdomains**
   - All discovered subdomains
   - Source: bug_bounty_monitor

4. **In-Scope Items**
   - URLs
   - Subdomains
   - IP ranges
   - Source: bug_bounty_monitor

5. **Scope Changes**
   - New apex domains
   - New subdomains
   - Removed items
   - Timestamps

### BBRF Client API

```python
from recon_tools.bbrf_client import BBRFClient

# Initialize
config = {
    'enabled': True,
    'api_endpoint': 'http://localhost:5000',
    'api_key': 'YOUR_API_KEY',
    'workspace': 'subfluxgpt'
}
client = BBRFClient(config)

# Create program
client.create_program('example.com', metadata={'platform': 'hackerone'})

# Add domain
client.add_domain('example.com', 'example.com', source='subfluxgpt')

# Add subdomain
client.add_subdomain('example.com', 'api.example.com', source='subfluxgpt')

# Add URL
client.add_url('example.com', 'https://api.example.com/users', 200, source='subfluxgpt')

# Add vulnerability
client.add_vulnerability('example.com', {
    'type': 'SQL Injection',
    'severity': 'critical',
    'url': 'https://api.example.com/users'
})

# Get data
domains = client.get_domains('example.com')
subdomains = client.get_subdomains('example.com')
```

### BBRF CLI Wrapper

```python
from recon_tools.bbrf_client import BBRFCLI

# Initialize
config = {'enabled': True, 'workspace': 'subfluxgpt'}
cli = BBRFCLI(config)

# Create scope
cli.new_scope('example.com')

# Add to scope
cli.scope_add('api.example.com')

# List domains
cli.domains()

# List subdomains
cli.subdomains()

# List URLs
cli.urls()

# Check if in scope
cli.inscope('api.example.com')
```

---

## Complete Monitoring Workflow

### 1. Start Monitoring with All Features

```bash
# Start with BBRF, folder organization, and auto recon
subfluxgpt monitor-start \
  --interval 3600 \
  --organize-folders \
  --auto-recon \
  --enable-bbrf \
  --bbrf-endpoint http://localhost:5000 \
  --bbrf-api-key YOUR_API_KEY \
  --output-dir targets/
```

This will:
- ✅ Monitor bug bounty platforms every hour
- ✅ Create folders by company automatically
- ✅ Automatically run recon on new programs
- ✅ Save all data to BBRF
- ✅ Feed results to learning system
- ✅ Organize results in structured folders

### 2. Check Status

```bash
subfluxgpt monitor-status
```

### 3. Stop Monitoring

```bash
subfluxgpt monitor-stop
```

### 4. Resume Monitoring

```bash
subfluxgpt monitor-start
```

---

## BBRF Server Setup

### Install BBRF Server

```bash
# Clone BBRF
git clone https://github.com/hacksider/BBRF-server.git
cd BBRF-server

# Install dependencies
pip install -r requirements.txt

# Configure
cp config.example.json config.json
# Edit config.json with your settings

# Start server
python3 app.py
```

### Configure BBRF

```json
{
  "host": "0.0.0.0",
  "port": 5000,
  "debug": false,
  "secret_key": "your-secret-key",
  "database": {
    "type": "sqlite",
    "path": "bbrf.db"
  },
  "auth": {
    "enabled": true,
    "api_keys": {
      "subfluxgpt": "your-api-key"
    }
  }
}
```

### Set Environment Variable

```bash
# Add to .zshrc
export BBRF_API_KEY="your-api-key"

# Reload shell
source ~/.zshrc
```

---

## BBRF Integration in Recon Tools

### Using BBRF in Custom Scripts

```python
from recon_tools.bbrf_client import BBRFClient
from ai_integration.tool_wrapper import ToolWrapper

# Initialize
bbrf_config = {
    'enabled': True,
    'api_endpoint': 'http://localhost:5000',
    'api_key': 'YOUR_API_KEY',
    'workspace': 'subfluxgpt'
}
bbrf = BBRFClient(bbrf_config)
wrapper = ToolWrapper()

# Run recon
result = wrapper.execute_tool('subfinder', ['-d', 'example.com'], enable_ai=True)

# Save to BBRF
if result['success']:
    # Create program
    bbrf.create_program('example.com')

    # Add subdomains
    for line in result['stdout'].split('\n'):
        if line.strip():
            bbrf.add_subdomain('example.com', line.strip(), source='subfinder')
```

### BBRF + AI Integration

```python
from recon_tools.bbrf_client import BBRFClient
from ai_integration.tool_wrapper import ToolWrapper
from ai_integration.continuous_learner import ContinuousLearner

# Initialize
bbrf = BBRFClient({'enabled': True, 'api_key': 'YOUR_API_KEY'})
wrapper = ToolWrapper()
learner = ContinuousLearner()

# Run recon with AI
result = wrapper.execute_tool('nuclei', ['-u', 'example.com'], enable_ai=True)

# Save findings to BBRF
if result['success']:
    for finding in result['ai_analysis'].get('findings', []):
        if finding['severity'] in ['critical', 'high']:
            bbrf.add_vulnerability('example.com', {
                'type': finding['finding'],
                'severity': finding['severity'],
                'ai_analysis': finding
            })

            # Log to learning system
            learner.log_finding('nuclei', finding['finding'], finding['severity'], 'example.com')
```

---

## Summary

### BBRF Integration ✅

- BBRF is already integrated in SubFluxGPT
- Complete API client and CLI wrapper
- Automatic data saving from bug bounty monitor
- Manual BBRF operations available

### On/Off Switch ✅

- `subfluxgpt monitor-start` - Turn monitoring ON
- `subfluxgpt monitor-stop` - Turn monitoring OFF
- `subfluxgpt monitor-status` - Check status

### Complete Monitoring Workflow ✅

```bash
# Start with all features
subfluxgpt monitor-start \
  --interval 3600 \
  --organize-folders \
  --auto-recon \
  --enable-bbrf \
  --bbrf-api-key YOUR_API_KEY

# Check status
subfluxgpt monitor-status

# Stop monitoring
subfluxgpt monitor-stop
```

### BBRF Features ✅

- Automatic program creation
- Domain and subdomain tracking
- URL and vulnerability management
- Scope change tracking
- Data synchronization

---

*Last Updated: 2026-10-14*
