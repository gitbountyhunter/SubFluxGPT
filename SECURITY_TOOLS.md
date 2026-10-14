# Security Tools Integration

SubFluxGPT integrates with popular bug bounty reconnaissance tools for automated security scanning.

## Supported Tools

| Tool | Purpose | Link |
|------|---------|------|
| **httpx** | HTTP toolkit for probing alive web servers | https://github.com/projectdiscovery/httpx |
| **katana** | Web crawler for discovering endpoints | https://github.com/projectdiscovery/katana |
| **anew** | Deduplication tool for domains, URLs, etc. | https://github.com/projectdiscovery/anew |
| **gau** | GetAllUrls - URLs from wayback machine | https://github.com/lc/gau |
| **nuclei** | Vulnerability scanner with templates | https://github.com/projectdiscovery/nuclei |
| **naabu** | Fast port scanner | https://github.com/projectdiscovery/naabu |
| **dnsx** | DNS toolkit for resolution | https://github.com/projectdiscovery/dnsx |
| **massdns** | High-performance DNS resolver | https://github.com/blechschmidt/massdns |
| **amass** | Attack surface discovery and subdomain enumeration | https://github.com/owasp-amass/amass |
| **hakrawler** | Simple, fast web crawler | https://github.com/hakluke/hakrawler |
| **waybackurls** | Fetch URLs from wayback machine | https://github.com/verylazytech/VeryLazyWayBack |
| **subfinder** | Fast passive subdomain discovery | https://github.com/projectdiscovery/subfinder |
| **assetfinder** | Find domains and subdomains | https://github.com/tomnomnom/assetfinder |
| **crt.sh** | Certificate transparency log search | https://crt.sh |
| **ffuf** | Fast web fuzzer for directory discovery | https://github.com/ffuf/ffuf |
| **feroxbuster** | Fast content discovery tool | https://github.com/epi052/feroxbuster |
| **arjun** | Parameter discovery in web apps | https://github.com/s0md3v/Arjun |
| **subjs** | Find subdomains in JavaScript files | https://github.com/lc/subjs |

## Installation

### Method 1: Go Install (Recommended for ProjectDiscovery tools)

```bash
# Install Go tools
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/anew/cmd/anew@latest
go install -v github.com/projectdiscovery/nuclei/cmd/nuclei@latest
go install -v github.com/projectdiscovery/naabu/cmd/naabu@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# Add to PATH
export PATH=$PATH:$(go env GOPATH)/bin
```

### Method 2: Homebrew (macOS)

```bash
brew tap projectdiscovery/tap
brew install httpx katana anew nuclei naabu dnsx
```

### Method 3: Direct Binary Download

```bash
# Download binaries
wget https://github.com/projectdiscovery/httpx/releases/latest/download/httpx_macos_amd64.zip
unzip httpx_macos_amd64.zip
sudo mv httpx /usr/local/bin/

# Repeat for other tools
```

### Method 4: GAU Installation

```bash
# GAU is typically installed via Go
go install -v github.com/lc/gau/v2/cmd/gau@latest

# Or via script
curl -sL https://raw.githubusercontent.com/lc/gau/master/gau.sh | sh
```

### Method 5: MassDNS Installation

```bash
# Clone and build
git clone https://github.com/blechschmidt/massdns.git
cd massdns
make
sudo cp bin/massdns /usr/local/bin/

# Download resolvers
wget https://raw.githubusercontent.com/projectdiscovery/nuclei-templates/main/resolvers.txt -O /etc/resolvers.txt
```

### Method 6: Amass Installation

```bash
# Go install
go install -v github.com/owasp-amass/amass/v4/cmd/amass@latest

# Or via Homebrew (macOS)
brew install amass

# Or via Docker
docker pull caesar/amass
docker run --rm caesar/amass enum -passive -d example.com

# Or download release
wget https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_v4.2.0_linux_amd64.zip
unzip amass_v4.2.0_linux_amd64.zip
sudo mv amass /usr/local/bin/
```

### Method 7: Hakrawler Installation

```bash
# Go install
go install -v github.com/hakluke/hakrawler@latest

# Or via Homebrew (macOS)
brew install hakrawler

# Or download release
wget https://github.com/hakluke/hakrawler/releases/latest/download/hakrawler_macos_amd64.zip
unzip hakrawler_macos_amd64.zip
sudo mv hakrawler /usr/local/bin/
```

### Method 8: Waybackurls Installation

```bash
# Go install
go install -v github.com/verylazytech/VeryLazyWayBack/cmd/waybackurls@latest

# Or via script
curl -sL https://raw.githubusercontent.com/verylazytech/VeryLazyWayBack/main/install.sh | sh

# Or download release
wget https://github.com/verylazytech/VeryLazyWayBack/releases/latest/download/waybackurls_macos_amd64.zip
unzip waybackurls_macos_amd64.zip
sudo mv waybackurls /usr/local/bin/
```

### Method 9: Subfinder Installation

```bash
# Go install
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Or via Homebrew (macOS)
brew install subfinder

# Or download release
wget https://github.com/projectdiscovery/subfinder/releases/latest/download/subfinder_macos_amd64.zip
unzip subfinder_macos_amd64.zip
sudo mv subfinder /usr/local/bin/
```

### Method 10: Assetfinder Installation

```bash
# Go install
go install -v github.com/tomnomnom/assetfinder@latest

# Or via Homebrew (macOS)
brew install assetfinder

# Or download release
wget https://github.com/tomnomnom/assetfinder/releases/latest/download/assetfinder_macos_amd64.zip
unzip assetfinder_macos_amd64.zip
sudo mv assetfinder /usr/local/bin/
```

### Method 11: FFUF Installation

```bash
# Go install
go install -v github.com/ffuf/ffuf/v2/cmd/ffuf@latest

# Or via Homebrew (macOS)
brew install ffuf

# Or download release
wget https://github.com/ffuf/ffuf/releases/latest/download/ffuf_macos_amd64.zip
unzip ffuf_macos_amd64.zip
sudo mv ffuf /usr/local/bin/
```

### Method 12: Feroxbuster Installation

```bash
# Go install
go install -v github.com/epi052/feroxbuster@latest

# Or via Homebrew (macOS)
brew install feroxbuster

# Or via Cargo (Rust)
cargo install feroxbuster

# Or download release
wget https://github.com/epi052/feroxbuster/releases/latest/download/feroxbuster_macos_amd64.zip
unzip feroxbuster_macos_amd64.zip
sudo mv feroxbuster /usr/local/bin/
```

### Method 13: Arjun Installation

```bash
# Go install
go install -v github.com/s0md3v/Arjun@latest

# Or via pip
pip3 install arjun

# Or download release
wget https://github.com/s0md3v/Arjun/releases/latest/download/arjun_macos_amd64.zip
unzip arjun_macos_amd64.zip
sudo mv arjun /usr/local/bin/
```

### Method 14: Subjs Installation

```bash
# Go install
go install -v github.com/lc/subjs@latest

# Or via Homebrew (macOS)
brew install subjs

# Or download release
wget https://github.com/lc/subjs/releases/latest/download/subjs_macos_amd64.zip
unzip subjs_macos_amd64.zip
sudo mv subjs /usr/local/bin/
```

### Note: crt.sh
crt.sh is a web service and doesn't require installation. It's accessed via HTTP requests.

## Verification

Verify each tool is installed:

```bash
httpx -version
katana -version
anew -version
gau -version
nuclei -version
naabu -version
dnsx -version
massdns -h
amass version
hakrawler -version
waybackurls -version
subfinder -version
assetfinder -version
ffuf -version
feroxbuster -version
arjun -version
subjs -version
```

## Configuration

Enable tools in `config.yaml`:

```yaml
security_tools:
  httpx:
    enabled: true
    binary_path: httpx
    timeout: 300
    options:
      timeout: 10
      threads: 50

  katana:
    enabled: true
    binary_path: katana
    timeout: 300
    options:
      depth: 2
      rate_limit: 10

  # ... enable other tools as needed

  amass:
    enabled: true
    binary_path: amass
    timeout: 600
    options:
      timeout: 300
      include_unresolvable: false

  hakrawler:
    enabled: true
    binary_path: hakrawler
    timeout: 300
    options:
      depth: 3
      scope: "rdn"
      subs: true

  waybackurls:
    enabled: true
    binary_path: waybackurls
    timeout: 300
    options:
      no_subs: false

  subfinder:
    enabled: true
    binary_path: subfinder
    timeout: 300
    options:
      all: false
      threads: 10

  assetfinder:
    enabled: true
    binary_path: assetfinder
    timeout: 300
    options:
      ignore: ""

  crtsh:
    enabled: true
    timeout: 30

  ffuf:
    enabled: true
    binary_path: ffuf
    timeout: 600
    options:
      threads: 40
      extensions: "php,html,js"
      match_status: "200,301,302"

  feroxbuster:
    enabled: true
    binary_path: feroxbuster
    timeout: 600
    options:
      threads: 50
      extensions: "php,html,js"
      depth: 3

  arjun:
    enabled: true
    binary_path: arjun
    timeout: 300
    options:
      headers: ""

  subjs:
    enabled: true
    binary_path: subjs
    timeout: 300
    options: {}
```

## Usage

### Using Python API

```python
from recon_tools import SecurityToolManager

# Initialize with config
import yaml
with open('config.yaml') as f:
    config = yaml.safe_load(f)

manager = SecurityToolManager(config)

# Check available tools
available = manager.get_available_tools()
print(f"Available: {available}")

# Run full reconnaissance
results = manager.run_reconnaissance('example.com')

# Access specific tool results
httpx_results = results['tools']['httpx']
gau_results = results['tools']['gau']
```

### Using Individual Tools

```python
from recon_tools import HTTPX, Katana, Nuclei

# HTTPX
httpx = HTTPX({'enabled': True, 'binary_path': 'httpx'})
result = httpx.probe(['example.com', 'test.com'])

# Katana
katana = Katana({'enabled': True, 'binary_path': 'katana'})
result = katana.crawl('https://example.com')

# Nuclei
nuclei = Nuclei({'enabled': True, 'binary_path': 'nuclei'})
result = nuclei.scan_url('https://example.com')
```

### Using Command Line

```bash
# Run full reconnaissance
python3 run_recon.py --domain example.com

# Run with specific tools
python3 run_recon.py --domain example.com --tools httpx gau nuclei

# Sync results to BBRF
python3 run_recon.py --domain example.com --sync-bbrf

# Custom output file
python3 run_recon.py --domain example.com --output recon_example.json
```

## Tool-Specific Usage

### HTTPX

```python
from recon_tools import HTTPX

httpx = HTTPX({'enabled': True, 'binary_path': 'httpx'})

# Probe domains
result = httpx.probe(['example.com', 'api.example.com'])

# Crawl for endpoints
result = httpx.crawl('https://example.com', depth=2)
```

### Katana

```python
from recon_tools import Katana

katana = Katana({'enabled': True, 'binary_path': 'katana'})

# Crawl URL
result = katana.crawl('https://example.com', options={'depth': 3})
```

### Anew

```python
from recon_tools import Anew

anew = Anew({'enabled': True, 'binary_path': 'anew'})

# Deduplicate URLs
result = anew.deduplicate(['url1', 'url2', 'url1'], file_path='urls.txt')
```

### GAU

```python
from recon_tools import GAU

gau = GAU({'enabled': True, 'binary_path': 'gau'})

# Get URLs from wayback
result = gau.get_urls('example.com', options={'threads': 10})
```

### Nuclei

```python
from recon_tools import Nuclei

nuclei = Nuclei({'enabled': True, 'binary_path': 'nuclei'})

# Scan URL
result = nuclei.scan_url('https://example.com')

# Scan multiple targets
result = nuclei.scan(['example.com', 'test.com'])
```

### Naabu

```python
from recon_tools import Naabu

naabu = Naabu({'enabled': True, 'binary_path': 'naabu'})

# Scan ports
result = naabu.scan(['example.com'])
```

### DNSX

```python
from recon_tools import DNSX

dnsx = DNSX({'enabled': True, 'binary_path': 'dnsx'})

# Resolve domains
result = dnsx.resolve(['example.com', 'api.example.com'])
```

### MassDNS

```python
from recon_tools import MassDNS

massdns = MassDNS({
    'enabled': True,
    'binary_path': 'massdns',
    'resolvers_file': '/etc/resolvers.txt'
})

# Resolve domains
result = massdns.resolve(['example.com', 'test.com'])
```

### Amass

```python
from recon_tools import Amass

amass = Amass({'enabled': True, 'binary_path': 'amass'})

# Enumerate subdomains
result = amass.enum('example.com')

# Gather intelligence
result = amass.intel('example.com')
```

### Hakrawler

```python
from recon_tools import Hakrawler

hakrawler = Hakrawler({'enabled': True, 'binary_path': 'hakrawler'})

# Crawl URL
result = hakrawler.crawl('https://example.com')

# Crawl with options
result = hakrawler.crawl('https://example.com', options={'depth': 5, 'subs': True})
```

### Waybackurls

```python
from recon_tools import Waybackurls

waybackurls = Waybackurls({'enabled': True, 'binary_path': 'waybackurls'})

# Get URLs from wayback
result = waybackurls.get_urls('example.com')

# Get URLs without subdomains
result = waybackurls.get_urls('example.com', options={'no_subs': True})
```

### Subfinder

```python
from recon_tools import Subfinder

subfinder = Subfinder({'enabled': True, 'binary_path': 'subfinder'})

# Enumerate subdomains
result = subfinder.enum('example.com')

# Enumerate with all sources
result = subfinder.enum('example.com', options={'all': True, 'threads': 20})
```

### Assetfinder

```python
from recon_tools import Assetfinder

assetfinder = Assetfinder({'enabled': True, 'binary_path': 'assetfinder'})

# Find domains and subdomains
result = assetfinder.find('example.com')

# Find with ignore pattern
result = assetfinder.find('example.com', options={'ignore': '*.test.com'})
```

### Crtsh

```python
from recon_tools import Crtsh

crtsh = Crtsh({'enabled': True})

# Query crt.sh for subdomains
result = crtsh.query('example.com')
```

### FFUF

```python
from recon_tools import FFUF

ffuf = FFUF({'enabled': True, 'binary_path': 'ffuf'})

# Fuzz a URL
result = ffuf.fuzz('http://example.com/FUZZ', '/usr/share/wordlists/dirb/common.txt')

# Fuzz with custom options
result = ffuf.fuzz(
    'http://example.com/FUZZ',
    '/usr/share/wordlists/dirb/common.txt',
    options={'threads': 100, 'extensions': 'php,html,js'}
)
```

### Feroxbuster

```python
from recon_tools import Feroxbuster

feroxbuster = Feroxbuster({'enabled': True, 'binary_path': 'feroxbuster'})

# Scan for directories
result = feroxbuster.scan('http://example.com', '/usr/share/wordlists/dirb/common.txt')

# Scan with depth
result = feroxbuster.scan(
    'http://example.com',
    '/usr/share/wordlists/dirb/common.txt',
    options={'depth': 5, 'extensions': 'php,html,js'}
)
```

### Arjun

```python
from recon_tools import Arjun

arjun = Arjun({'enabled': True, 'binary_path': 'arjun'})

# Discover parameters
result = arjun.discover('https://example.com/page?id=1')

# Discover with custom headers
result = arjun.discover('https://example.com/page', options={'headers': 'Authorization: Bearer token'})
```

### Subjs

```python
from recon_tools import Subjs

subjs = Subjs({'enabled': True, 'binary_path': 'subjs'})

# Extract subdomains from JS files
result = subjs.extract([
    'https://example.com/app.js',
    'https://example.com/main.js'
])
```

## BBRF Integration

### Setup BBRF

```bash
# Install BBRF CLI
npm install -g @hackerone/bbrf-cli

# Or use Docker
docker pull hackerone/bbrf
```

### Configure BBRF

```yaml
bbrf:
  enabled: true
  api_endpoint: http://localhost:5000
  api_key: ${BBRF_API_KEY}
  workspace: subfluxgpt
  username: subfluxgpt
```

### Use BBRF with SubFluxGPT

```python
from recon_tools import BBRFClient

bbrf = BBRFClient({
    'enabled': True,
    'api_endpoint': 'http://localhost:5000',
    'api_key': 'your-key',
    'workspace': 'subfluxgpt'
})

# Create program
bbrf.create_program('example.com')

# Add findings
bbrf.add_domain('example.com', 'example.com', source='subfluxgpt')
bbrf.add_subdomain('example.com', 'api.example.com', source='amass')
bbrf.add_url('example.com', 'https://api.example.com/', 200, source='httpx')
bbrf.add_vulnerability('example.com', {
    'type': 'subdomain_takeover',
    'severity': 'high'
})
```

## Complete Workflow

```bash
# 1. Enable tools in config.yaml
# 2. Install tools (see Installation section)
# 3. Run reconnaissance
python3 run_recon.py --domain example.com --sync-bbrf

# 4. Analyze with AI
curl -X POST http://localhost:8000/analyze_domain \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "model": "gpt2_124M"}'

# 5. Run benchmark
python3 run_benchmark.py --domain example.com --compare
```

## Troubleshooting

### Tool Not Found

If you get "command not found":
- Ensure the tool is installed
- Check it's in your PATH: `which httpx`
- Add to PATH if needed: `export PATH=$PATH:/path/to/tool`

### Permission Denied

If you get permission errors:
- Make tool executable: `chmod +x /path/to/tool`
- Install to /usr/local/bin or add to PATH

### Timeout Errors

If tools timeout:
- Increase timeout in config.yaml
- Check tool is working independently
- Reduce concurrent operations

### BBRF Connection Errors

If BBRF fails to connect:
- Ensure BBRF server is running
- Check API endpoint in config.yaml
- Verify API key is correct

## Best Practices

1. **Rate Limiting**: Always use rate limiting to avoid being blocked
2. **Timeouts**: Set appropriate timeouts for each tool
3. **Output Parsing**: Validate JSON output before processing
4. **Error Handling**: Always check tool availability before use
5. **Deduplication**: Use anew to avoid duplicate findings
6. **BBRF Sync**: Regularly sync findings to BBRF for tracking
7. **Templates**: Keep nuclei templates updated
8. **Resolvers**: Use reliable DNS resolvers for massdns

## Security Considerations

- Never commit API keys or sensitive data
- Use environment variables for secrets
- Validate all tool inputs
- Scan only targets you have permission to test
- Keep tools updated for security patches
- Use BBRF for secure data sharing

## References

- ProjectDiscovery Tools: https://projectdiscovery.io/
- BBRF Documentation: https://github.com/hackerone/bbrf-cli
- SubFluxGPT Commands: [COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md)
