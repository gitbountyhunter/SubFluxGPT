# AI Workflows Documentation

Complete guide to AI-powered workflows for all security tools in SubFluxGPT.

## Table of Contents
1. [Overview](#overview)
2. [AI-Integrated Tools](#ai-integrated-tools)
3. [Pipe Workflows](#pipe-workflows)
4. [Continuous Learning Workflows](#continuous-learning-workflows)
5. [Self-Improving Workflows](#self-improving-workflows)
6. [Bug Bounty Monitoring Workflows](#bug-bounty-monitoring-workflows)
7. [Advanced Examples](#advanced-examples)

---

## Overview

SubFluxGPT integrates AI into **every single security tool** to provide:
- Real-time analysis of tool outputs
- Intelligent command suggestions
- Pattern recognition and anomaly detection
- Continuous learning from workflows
- Automated vulnerability prioritization

### Supported Tools (14+)

| Tool | Purpose | AI Tasks |
|------|---------|----------|
| httpx | HTTP probing | Tech stack detection, vulnerability analysis |
| subfinder | Subdomain discovery | Classification, takeover prediction |
| katana | Web crawling | Endpoint extraction, parameter analysis |
| nuclei | Vulnerability scanning | Finding prioritization, chain analysis |
| bbrf | Data management | Correlation, pattern detection |
| dnsx | DNS resolution | Wildcard detection, suspicious analysis |
| massdns | Mass DNS | Resolution pattern analysis |
| naabu | Port scanning | Service detection, vulnerability prediction |
| gau | URL archives | Historical analysis, parameter extraction |
| waybackurls | Wayback Machine | Historical analysis, live detection |
| ffuf | Fuzzing | Anomaly detection, wordlist suggestion |
| hakrawler | Crawling | JS extraction, endpoint discovery |
| assetfinder | Asset discovery | Asset classification, scope analysis |
| amass | Comprehensive recon | Attack surface analysis, correlation |

---

## AI-Integrated Tools

### Using the Tool Wrapper

```python
from ai_integration.tool_wrapper import ToolWrapper

# Initialize wrapper
wrapper = ToolWrapper(model_path='models/gpt2_124M.gguf', enable_learning=True)

# Execute tool with AI analysis
result = wrapper.execute_tool(
    tool_name='httpx',
    args=['-u', 'example.com', '-silent', '-json'],
    enable_ai=True
)

# Result includes:
# - stdout: Tool output
# - ai_analysis: AI insights
# - success: Execution status
print(result['ai_analysis'])
```

### Example: HTTPX with AI

```bash
# Standard httpx
httpx -u example.com -silent -json

# AI-enhanced httpx
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('httpx', ['-u', 'example.com', '-silent'], enable_ai=True)
print(json.dumps(result['ai_analysis'], indent=2))
"
```

AI Output:
```json
{
  "method": "pattern_based",
  "tool": "httpx",
  "task": "detect_tech_stack",
  "findings": [
    {
      "category": "server",
      "technology": "nginx",
      "confidence": "medium"
    },
    {
      "category": "cdn",
      "technology": "cloudflare",
      "confidence": "high"
    }
  ]
}
```

### Example: Subfinder with AI

```bash
# AI-enhanced subdomain discovery
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('subfinder', ['-d', 'example.com', '-silent'], enable_ai=True)
print(json.dumps(result['ai_analysis'], indent=2))
"
```

AI Output:
```json
{
  "method": "pattern_based",
  "tool": "subfinder",
  "task": "classify_subdomains",
  "findings": [
    {
      "domain": "dev.example.com",
      "type": "dev",
      "confidence": "high"
    },
    {
      "domain": "api.example.com",
      "type": "prod",
      "confidence": "high"
    },
    {
      "domain": "cdn.example.com",
      "type": "cdn",
      "confidence": "high"
    }
  ]
}
```

### Example: Nuclei with AI

```bash
# AI-enhanced vulnerability scanning
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('nuclei', ['-u', 'example.com', '-silent', '-json'], enable_ai=True)
print(json.dumps(result['ai_analysis'], indent=2))
"
```

AI Output:
```json
{
  "method": "pattern_based",
  "tool": "nuclei",
  "task": "prioritize_findings",
  "findings": [
    {
      "finding": "SQL Injection detected",
      "severity": "critical"
    },
    {
      "finding": "Information disclosure",
      "severity": "medium"
    },
    {
      "finding": "Missing security headers",
      "severity": "low"
    }
  ]
}
```

---

## Pipe Workflows

### Basic Pipe Workflow

```bash
# Pipe subfinder to httpx with AI analysis
subfinder -d example.com -silent | \
  python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
import sys
wrapper = ToolWrapper()
for line in sys.stdin:
    result = wrapper.execute_tool('httpx', ['-silent', '-json'], enable_ai=True)
    print(result['ai_analysis'])
"
```

### Advanced Pipe Workflow

```python
from ai_integration.tool_wrapper import ToolWrapper

wrapper = ToolWrapper()

# Define pipeline
pipeline = [
    {'tool': 'subfinder', 'args': ['-d', 'example.com', '-silent']},
    {'tool': 'httpx', 'args': ['-silent', '-json']},
    {'tool': 'nuclei', 'args': ['-silent', '-json']}
]

# Execute pipeline
results = wrapper.pipe_workflow(pipeline, enable_ai=True)

# Results include AI analysis at each step
for step in results['steps']:
    print(f"{step['tool']}: {step.get('ai_analysis', {})}")
```

### Example: Full Recon Pipeline

```bash
# Complete recon with AI at every step
subfinder -d example.com -silent | \
  httpx -silent -json | \
  jq -r '.url' | \
  katana -silent -json | \
  python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
result = wrapper.execute_tool('nuclei', ['-silent', '-json'], enable_ai=True)
print(result['ai_analysis'])
"
```

---

## Continuous Learning Workflows

### Enable Continuous Learning

```bash
# Start learning daemon
subfluxgpt learn --start

# This runs in background and learns from:
# - Every command you run
# - Every tool output
# - Every workflow pattern
# - Every security finding
```

### Manual Learning Entry

```python
from ai_integration.continuous_learner import ContinuousLearner

learner = ContinuousLearner()

# Log a command
learner.log_command(
    tool='httpx',
    args=['-u', 'example.com'],
    exit_code=0,
    duration=2.5
)

# Log tool output
learner.log_tool_output(
    tool='httpx',
    command='httpx -u example.com',
    stdout='200 OK https://example.com',
    stderr='',
    analyze=True
)

# Log a finding
learner.log_finding(
    tool='nuclei',
    finding_type='xss',
    severity='high',
    target='https://example.com/search',
    verified=True
)

# Log a workflow
learner.log_workflow(
    tool_sequence=['subfinder', 'httpx', 'nuclei'],
    success=True
)
```

### Export Training Data

```python
from ai_integration.continuous_learner import ContinuousLearner

learner = ContinuousLearner()

# Export for fine-tuning
learner.export_training_dataset('data/training_dataset.json')

# Get learning statistics
stats = learner.get_learning_stats()
print(json.dumps(stats, indent=2))
```

---

## Self-Improving Workflows

### Start Self-Improving LLM

```bash
# Feed bug bounty reports to mini AIs
subfluxgpt learn --start

# This:
# - Fetches HackerOne/Bugcrowd reports
# - Processes them into training examples
# - Fine-tunes models automatically
# - Improves intelligence over time
```

### Manual Report Feeding

```python
from self_improving_llm import SelfImprovingLLM

system = SelfImprovingLLM()

# Fetch reports manually
system.fetch_reports()

# Process into training examples
system.process_reports()

# Update models
system.update_models()
```

### View Learning Progress

```bash
# Check self-improving statistics
python3 -c "
from self_improving_llm import SelfImprovingLLM
system = SelfImprovingLLM()
stats = system.get_learning_stats()
print(json.dumps(stats, indent=2))
"
```

Output:
```json
{
  "total_reports": 1523,
  "processed_reports": 1498,
  "total_examples": 8976,
  "examples_by_type": {
    "severity_classification": 2244,
    "vulnerability_classification": 2244,
    "summarization": 2244,
    "command_suggestion": 2244
  },
  "reports_by_platform": {
    "hackerone": 1023,
    "bugcrowd": 500
  }
}
```

---

## Bug Bounty Monitoring Workflows

### Start Platform Monitor

```bash
# Monitor bug bounty platforms for new programs and scope changes
subfluxgpt monitor --interval 3600

# This:
# - Checks HackerOne, Bugcrowd, YesWeHack, Intigriti
# - Detects new companies
# - Detects scope changes
# - Triggers SubFluxGPT automatically
```

### Check Once

```bash
# Check platforms once
subfluxgpt monitor --check-once
```

### List New Programs

```bash
# List newly discovered programs
subfluxgpt monitor --list-new
```

### List Recent Changes

```bash
# List scope changes in last 24 hours
subfluxgpt monitor --list-changes 24
```

### Manual Trigger

```python
from bug_bounty_monitor import BugBountyMonitor

monitor = BugBountyMonitor()

# Check all platforms
monitor.check_all_platforms()

# Get new programs
new_programs = monitor.get_new_programs(limit=50)

# Get recent changes
changes = monitor.get_recent_changes(hours=24)
```

---

## Advanced Examples

### Example 1: Full AI-Powered Recon

```bash
#!/bin/bash
# ai_recon.sh - Full AI-powered reconnaissance

DOMAIN=$1

echo "[*] Starting AI-powered recon on $DOMAIN"

# Subdomain discovery with AI
echo "[*] Discovering subdomains..."
subfinder -d $DOMAIN -silent | \
  python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
import sys
wrapper = ToolWrapper()
for line in sys.stdin:
    line = line.strip()
    if line:
        result = wrapper.execute_tool('httpx', ['-silent', '-json'], enable_ai=True)
        print(f\"{line}: {result['ai_analysis']}\")
" > subdomain_analysis.txt

# Crawl with AI
echo "[*] Crawling with AI..."
katana -u https://$DOMAIN -silent -json | \
  python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
import sys
wrapper = ToolWrapper()
for line in sys.stdin:
    result = wrapper.execute_tool('nuclei', ['-silent', '-json'], enable_ai=True)
    print(result['ai_analysis'])
" > vulnerability_analysis.txt

echo "[*] Complete! Check subdomain_analysis.txt and vulnerability_analysis.txt"
```

Usage:
```bash
chmod +x ai_recon.sh
./ai_recon.sh example.com
```

### Example 2: AI-Assisted Bug Hunting

```python
#!/usr/bin/env python3
# ai_bug_hunter.py - AI-assisted bug hunting

from ai_integration.tool_wrapper import ToolWrapper
from ai_integration.continuous_learner import ContinuousLearner
import json

class AIBugHunter:
    def __init__(self):
        self.wrapper = ToolWrapper()
        self.learner = ContinuousLearner()

    def hunt(self, domain):
        print(f"[*] Hunting on {domain}")

        # Step 1: Subdomain discovery
        print("[*] Discovering subdomains...")
        subfinder_result = self.wrapper.execute_tool(
            'subfinder', ['-d', domain, '-silent'], enable_ai=True
        )
        self.learner.log_command('subfinder', ['-d', domain], 0, 5.0)

        # Step 2: HTTP probing
        print("[*] Probing HTTP...")
        httpx_result = self.wrapper.execute_tool(
            'httpx', ['-silent', '-json'], enable_ai=True
        )

        # Step 3: Vulnerability scanning
        print("[*] Scanning for vulnerabilities...")
        nuclei_result = self.wrapper.execute_tool(
            'nuclei', ['-silent', '-json'], enable_ai=True
        )

        # Step 4: Analyze findings
        print("[*] Analyzing findings...")
        for finding in nuclei_result.get('ai_analysis', {}).get('findings', []):
            if finding['severity'] in ['critical', 'high']:
                print(f"[!] {finding['severity']}: {finding['finding']}")
                self.learner.log_finding(
                    'nuclei',
                    finding['finding'],
                    finding['severity'],
                    domain
                )

        # Step 5: Log workflow
        self.learner.log_workflow(
            ['subfinder', 'httpx', 'nuclei'],
            success=True
        )

if __name__ == '__main__':
    import sys
    hunter = AIBugHunter()
    hunter.hunt(sys.argv[1])
```

Usage:
```bash
python3 ai_bug_hunter.py example.com
```

### Example 3: Continuous AI Learning Loop

```bash
#!/bin/bash
# continuous_ai_loop.sh - Continuous AI learning and recon

# Start learning daemon
subfluxgpt learn --start &
LEARNING_PID=$!

# Start monitoring
subfluxgpt monitor --interval 3600 &
MONITOR_PID=$!

# Run recon on target list
for domain in $(cat targets.txt); do
    echo "[*] Running recon on $domain"
    subfluxgpt recon --domain $domain --verbose

    # Learning happens automatically in background
done

# Stop daemons
kill $LEARNING_PID
kill $MONITOR_PID

# Check learning progress
python3 -c "
from ai_integration.continuous_learner import ContinuousLearner
learner = ContinuousLearner()
print(json.dumps(learner.get_learning_stats(), indent=2))
"
```

### Example 4: Custom AI Analysis

```python
#!/usr/bin/env python3
# custom_ai_analysis.py - Custom AI analysis workflows

from ai_integration.tool_wrapper import ToolWrapper
from ai_integration.ai_analyzer import AIAnalyzer
import json

class CustomAIAnalysis:
    def __init__(self):
        self.wrapper = ToolWrapper()
        self.analyzer = AIAnalyzer()

    def analyze_attack_surface(self, domain):
        """Complete attack surface analysis with AI"""

        results = {
            'domain': domain,
            'timestamp': str(datetime.now()),
            'analysis': {}
        }

        # Subdomain analysis
        subfinder_result = self.wrapper.execute_tool(
            'subfinder', ['-d', domain, '-silent'], enable_ai=True
        )
        results['analysis']['subdomains'] = subfinder_result['ai_analysis']

        # Tech stack analysis
        httpx_result = self.wrapper.execute_tool(
            'httpx', ['-u', f'https://{domain}', '-silent'], enable_ai=True
        )
        results['analysis']['tech_stack'] = httpx_result['ai_analysis']

        # Vulnerability analysis
        nuclei_result = self.wrapper.execute_tool(
            'nuclei', ['-u', f'https://{domain}', '-silent'], enable_ai=True
        )
        results['analysis']['vulnerabilities'] = nuclei_result['ai_analysis']

        # DNS analysis
        dnsx_result = self.wrapper.execute_tool(
            'dnsx', ['-d', domain, '-silent'], enable_ai=True
        )
        results['analysis']['dns'] = dnsx_result['ai_analysis']

        return results

    def prioritize_targets(self, domains):
        """Prioritize domains based on AI analysis"""

        prioritized = []

        for domain in domains:
            analysis = self.analyze_attack_surface(domain)

            # Calculate risk score
            risk_score = 0
            if analysis['analysis']['vulnerabilities']['findings']:
                for finding in analysis['analysis']['vulnerabilities']['findings']:
                    if finding['severity'] == 'critical':
                        risk_score += 10
                    elif finding['severity'] == 'high':
                        risk_score += 5
                    elif finding['severity'] == 'medium':
                        risk_score += 2

            prioritized.append({
                'domain': domain,
                'risk_score': risk_score,
                'analysis': analysis
            })

        # Sort by risk score
        prioritized.sort(key=lambda x: x['risk_score'], reverse=True)

        return prioritized

if __name__ == '__main__':
    analyzer = CustomAIAnalysis()

    # Single domain analysis
    results = analyzer.analyze_attack_surface('example.com')
    print(json.dumps(results, indent=2))

    # Prioritize multiple domains
    domains = ['example.com', 'test.com', 'demo.com']
    prioritized = analyzer.prioritize_targets(domains)
    print(json.dumps(prioritized, indent=2))
```

---

## Best Practices

### 1. Always Enable AI Analysis

```bash
# Bad
httpx -u example.com

# Good
python3 -c "
from ai_integration.tool_wrapper import ToolWrapper
wrapper = ToolWrapper()
wrapper.execute_tool('httpx', ['-u', 'example.com'], enable_ai=True)
"
```

### 2. Use Pipe Workflows

```bash
# Connect tools with AI at each step
subfinder -d example.com | \
  httpx -silent | \
  nuclei -silent
```

### 3. Keep Learning Running

```bash
# Always have learning in background
subfluxgpt learn --start &
```

### 4. Monitor Bug Bounty Platforms

```bash
# Always monitor for new programs
subfluxgpt monitor --interval 3600 &
```

### 5. Fine-Tune Regularly

```bash
# Fine-tune after collecting data
subfluxgpt fine-tune --prepare-dataset
subfluxgpt fine-tune --finetune --dataset data/datasets/bugbounty_finetune
```

---

## Summary

SubFluxGPT's AI workflows provide:
- ✅ AI analysis on every tool output
- ✅ Continuous learning from every command
- ✅ Self-improving models from bug reports
- ✅ Automatic monitoring of bug bounty platforms
- ✅ Intelligent prioritization and suggestions

**Key Commands**:
- `subfluxgpt learn` - Start continuous learning
- `subfluxgpt monitor` - Monitor bug bounty platforms
- `subfluxgpt fine-tune` - Fine-tune with Unsloth
- Tool wrapper for AI-enhanced tool execution

**Next Steps**:
1. Start learning: `subfluxgpt learn --start`
2. Start monitoring: `subfluxgpt monitor --interval 3600`
3. Use AI wrapper in your scripts
4. Fine-tune models with collected data

---

*Last Updated: 2026-10-14*
*System: Mac (32GB RAM, 8-core, 19 CPU)*
