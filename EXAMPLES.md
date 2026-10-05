# SubFluxGPT Usage Examples

This document provides detailed examples of how to use SubFluxGPT in various bug bounty workflows.

## Basic Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Example Workflows

### Workflow 1: Basic Subdomain Generation

Generate new subdomains from existing ones using Gemini (free tier):

```bash
# Input file: known_subs.txt
api.example.com
staging.example.com
admin.example.com
dev.example.com

# Run SubFluxGPT
subfluxgpt -i known_subs.txt -o new_subs.txt --api gemini

# Output: new_subs.txt
test.example.com
prod.example.com
auth.example.com
...
```

### Workflow 2: DNS Resolution + Validation

Generate and validate subdomains with DNS resolution:

```bash
subfluxgpt -i known_subs.txt -o resolved_subs.txt --api gemini --resolve
```

This will:
1. Generate subdomains using AI
2. Check for wildcard DNS
3. Resolve each subdomain
4. Output only successfully resolved subdomains

### Workflow 3: HTTP Probing Integration

Probe generated subdomains with HTTP and pipe to httpx:

```bash
subfluxgpt -i known_subs.txt --api gemini --resolve --probe | httpx -status-code -title -tech-detect
```

This workflow:
1. Generates subdomains
2. Resolves them
3. Probes with HTTP
4. Pipes live subdomains to httpx for detailed analysis

### Workflow 4: BBRF Integration

Directly inject AI-generated subdomains into BBRF:

```bash
# Basic BBRF injection
subfluxgpt -i known_subs.txt --api gemini | bbrf domain add -

# With program scoping
subfluxgpt -i known_subs.txt --api gemini --bbrf-program target_program

# With scope checking
subfluxgpt -i known_subs.txt --api gemini --bbrf-program target_program --bbrf-scope-check
```

### Workflow 5: Netlas Attack Surface Enrichment

Enrich subdomains with Netlas data:

```bash
# Basic enrichment
subfluxgpt -i known_subs.txt --api gemini --netlas-enrich -o enriched.json

# Custom Netlas dork
subfluxgpt -i known_subs.txt --api gemini --netlas-dork "domain:example.com port:443" -o results.json
```

### Workflow 6: Multi-API Fallback

Use multiple APIs with automatic fallback:

```bash
# Try Gemini, fallback to Claude
subfluxgpt -i known_subs.txt --api gemini --fallback claude

# Fallback chain: Gemini -> Claude -> OpenAI
subfluxgpt -i known_subs.txt --api gemini --fallback claude,openai
```

### Workflow 7: Complete Bug Bounty Pipeline

Full workflow from enumeration to analysis:

```bash
# Step 1: Generate with AI
subfluxgpt -i known_subs.txt -o ai_generated.txt --api gemini

# Step 2: Resolve and filter
subfluxgpt -i ai_generated.txt -o resolved.txt --api gemini --resolve

# Step 3: Probe with HTTP
subfluxgpt -i resolved.txt -o alive.txt --api gemini --probe

# Step 4: Enrich with Netlas
subfluxgpt -i alive.txt --api gemini --netlas-enrich

# Step 5: Inject into BBRF
subfluxgpt -i alive.txt --api gemini --bbrf-program target_program

# Step 6: Final analysis with httpx
cat alive.txt | httpx -status-code -title -tech-detect -screenshot
```

### Workflow 8: Combining with Traditional Tools

Use SubFluxGPT alongside traditional subdomain tools:

```bash
# Traditional enumeration
subfinder -d example.com > subfinder.txt
amass enum -d example.com > amass.txt

# Merge results
cat subfinder.txt amass.txt | sort -u > traditional.txt

# AI-powered generation
subfluxgpt -i traditional.txt -o ai_enhanced.txt --api gemini

# Merge all
cat traditional.txt ai_enhanced.txt | sort -u > final_subs.txt

# Resolve and probe
cat final_subs.txt | httpx -status-code -title
```

### Workflow 9: Output in Different Formats

Export results in various formats:

```bash
# Text format (default)
subfluxgpt -i known_subs.txt -o output.txt --api gemini --format text

# JSON format
subfluxgpt -i known_subs.txt -o output.json --api gemini --format json

# CSV format
subfluxgpt -i known_subs.txt -o output.csv --api gemini --format csv
```

### Workflow 10: Wildcard Handling

Handle wildcard DNS domains:

```bash
# Enable wildcard check (default)
subfluxgpt -i known_subs.txt --api gemini --resolve --wildcard-check

# Disable wildcard check
subfluxgpt -i known_subs.txt --api gemini --resolve --no-wildcard-check
```

## Advanced Examples

### Custom Token Count

Generate more or fewer subdomains:

```bash
# Generate 100 subdomains
subfluxgpt -i known_subs.txt --api gemini --count 100

# Generate 25 subdomains
subfluxgpt -i known_subs.txt --api gemini --count 25
```

### Concurrent Operations

Adjust concurrency for performance:

```bash
# High concurrency (faster but more resource intensive)
subfluxgpt -i known_subs.txt --api gemini --resolve --concurrent 100

# Low concurrency (slower but more stable)
subfluxgpt -i known_subs.txt --api gemini --resolve --concurrent 10
```

### Both HTTP Schemes

Probe both HTTP and HTTPS:

```bash
subfluxgpt -i known_subs.txt --api gemini --probe --probe-scheme both
```

## Tips and Best Practices

1. **Start with Gemini**: Use Gemini for free tier and generous context window
2. **Use fallbacks**: Configure fallback APIs for reliability
3. **Pipeline to stdout**: Design workflows that pipe to other tools
4. **Check wildcards**: Always enable wildcard detection for accuracy
5. **Combine tools**: Use SubFluxGPT alongside traditional tools
6. **Batch processing**: Process large files in chunks for stability
7. **BBRF integration**: Use BBRF for organized bug bounty workflows
8. **Netlas enrichment**: Leverage Netlas for attack surface analysis

## Troubleshooting

### API Rate Limits

If you hit rate limits:

```bash
# Use fallback APIs
subfluxgpt -i known_subs.txt --api gemini --fallback claude,openai

# Reduce concurrent requests
subfluxgpt -i known_subs.txt --api gemini --concurrent 10
```

### Memory Issues

For large subdomain lists:

```bash
# Process in chunks
split -l 1000 large_file.txt chunk_
for chunk in chunk_*; do
    subfluxgpt -i $chunk -o output_$chunk --api gemini
done
cat output_* > final_output.txt
```

### DNS Resolution Failures

If DNS resolution fails:

```bash
# Check wildcard detection
subfluxgpt -i known_subs.txt --api gemini --resolve --wildcard-check

# Skip resolution and use external resolver
subfluxgpt -i known_subs.txt --api gemini --dont-resolve | dnsx -silent
```

## Integration Examples

### With Nuclei

```bash
subfluxgpt -i known_subs.txt --api gemini --resolve | nuclei -t cves/ -severity critical
```

### With Naabu

```bash
subfluxgpt -i known_subs.txt --api gemini --resolve | naabu -top-ports 1000
```

### With Katana

```bash
subfluxgpt -i known_subs.txt --api gemini --probe | katana -depth 2 -jc
```

---

For more information, see the main [README.md](README.md) file.
