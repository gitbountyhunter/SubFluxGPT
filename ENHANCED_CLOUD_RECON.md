# Enhanced Cloud Recon - Killer Features

## Overview

The Enhanced Cloud Recon module extends the basic SNI-IP range reconnaissance with powerful analysis capabilities for bug bounty researchers and security professionals.

## Killer Features

### 1. IP Resolution and ASN Lookup
- **Resolves domains to IP addresses** with parallel processing
- **ASN lookup** using ipinfo.io API
- **Cloud provider detection** (AWS, Google, Azure, DigitalOcean, Oracle)
- **Geolocation data** (country, city, region)
- **Organizational data** (ISP, organization name)

**Use Cases:**
- Identify which cloud providers are being used
- Map domain infrastructure
- Find non-cloud assets that might be overlooked
- Correlate domains with organizations

### 2. Port Scanning
- **Multi-port scanning** across common service ports (21 ports by default)
- **Parallel scanning** for speed
- **Service identification** (HTTP, SSH, MySQL, Redis, etc.)
- **Banner grabbing** where available
- **Categorization** of services (databases, remote access, web services, etc.)

**Use Cases:**
- Find exposed services
- Identify misconfigured ports
- Discover hidden services
- Prioritize targets based on open ports

**Default Ports Scanned:**
- FTP (21), SSH (22), Telnet (23), SMTP (25)
- DNS (53), HTTP (80), POP3 (110), IMAP (143)
- HTTPS (443), SMB (445), IMAPS (993), POP3S (995)
- MSSQL (1433), Oracle (1521), MySQL (3306), RDP (3389)
- PostgreSQL (5432), VNC (5900), Redis (6379)
- HTTP-Alt (8080), HTTPS-Alt (8443), Elasticsearch (9200), MongoDB (27017)

### 3. SSL/TLS Certificate Analysis
- **Certificate extraction** from HTTPS endpoints
- **Expiration tracking** with days-until-expiry
- **Issuer identification** (Let's Encrypt, DigiCert, etc.)
- **Self-signed detection**
- **Wildcard certificate identification**
- **SAN (Subject Alternative Names) extraction**
- **Signature algorithm and key size analysis**

**Use Cases:**
- Find expiring certificates (potential takeovers)
- Identify self-signed certificates (testing environments)
- Discover wildcard subdomains from SANs
- Assess certificate security (weak algorithms, small keys)

**Warnings Generated:**
- Certificates expiring within 30 days
- Expired certificates
- Self-signed certificates
- Wildcard certificates with coverage

### 4. Technology Fingerprinting
- **HTTP header analysis** for technology detection
- **Web server identification** (nginx, Apache, IIS, etc.)
- **Framework detection** (Django, Flask, Express, Rails, Laravel)
- **CDN detection** (Cloudflare, Akamai, Fastly, CloudFront)
- **Load balancer detection** (AWS ELB/ALB, HAProxy, nginx)
- **Cloud infrastructure identification**

**Use Cases:**
- Understand technology stack
- Identify cloud infrastructure usage
- Find assets behind CDNs
- Detect load balancers and WAFs

**Technologies Detected:**
- **Web Servers:** nginx, Apache, IIS, Cloudflare, Gunicorn, Caddy
- **Frameworks:** Django, Flask, Express, Rails, Laravel
- **CDNs:** Akamai, Fastly, CloudFront, Cloudflare
- **Load Balancers:** AWS ELB/ALB, HAProxy, nginx

### 5. Threat Intelligence Integration
- **Shodan API integration** for vulnerability data
- **Censys API integration** for service enumeration
- **Vulnerability tracking** with CVE IDs
- **Service enumeration** from threat intel
- **Risk scoring** based on open ports and vulnerabilities
- **Malware detection** via tags

**Use Cases:**
- Find known vulnerabilities
- Assess risk level
- Prioritize high-risk targets
- Discover services not visible from port scanning

**Note:** Requires API keys for Shodan and/or Censys

### 6. Historical Tracking
- **Timestamped snapshots** of all scans
- **Change detection** between scans
- **New domain discovery** tracking
- **Domain removal** tracking
- **Trend analysis** over time

**Use Cases:**
- Monitor infrastructure changes
- Detect new assets appearing
- Track asset retirement
- Identify suspicious changes

### 7. Comprehensive Reporting
- **Summary reports** with key findings
- **JSON export** for integration
- **Categorized results** by provider, technology, service
- **Risk assessments** and recommendations
- **Visual summaries** (ready for dashboard integration)

## Usage

### Basic Cloud Recon (Original)

```bash
# Download and process SNI data
python3 run_cloud_recon.py --download --process

# Filter by apex domain
python3 run_cloud_recon.py --download --process --apex dell.com

# Export for BountyCatch
python3 run_cloud_recon.py --export --project dell_recon
```

### Enhanced Cloud Recon (Killer Features)

```bash
# Run all killer features
python3 run_cloud_recon.py --enhanced --apex dell.com --project dell_recon

# Run specific features
python3 run_cloud_recon.py --enhanced --no-port --no-ssl --apex dell.com

# Enable threat intelligence (requires API keys)
python3 run_cloud_recon.py --enhanced --threat-intel --apex dell.com
```

### Module Usage

```python
from cloud_recon import EnhancedCloudRecon

# Initialize
recon = EnhancedCloudRecon(config_path='config.yaml')

# Run full enhanced recon
results = recon.run_killer_recon(
    apex_domain='dell.com',
    project_name='dell_recon',
    enable_ip_analysis=True,
    enable_port_scan=True,
    enable_ssl_analysis=True,
    enable_tech_fingerprint=True,
    enable_threat_intel=False  # Requires API keys
)

# Access results
print(results['summary']['key_findings'])
```

### Individual Module Usage

```python
from cloud_recon import IPAnalyzer, PortScanner, SSLAnalyzer, TechFingerprinter

# IP Analysis
ip_analyzer = IPAnalyzer()
cloud_assets = ip_analyzer.find_cloud_assets(['google.com', 'amazon.com'])
ip_report = ip_analyzer.generate_ip_report(cloud_assets)

# Port Scanning
port_scanner = PortScanner()
scan_results = port_scanner.scan_ips(['1.1.1.1', '8.8.8.8'])
scan_report = port_scanner.generate_scan_report(scan_results)

# SSL Analysis
ssl_analyzer = SSLAnalyzer()
certificates = ssl_analyzer.analyze_certificates(['google.com', 'github.com'])
ssl_report = ssl_analyzer.generate_certificate_report(certificates)

# Technology Fingerprinting
tech_fp = TechFingerprinter()
fingerprints = tech_fp.fingerprint_domains(['google.com', 'github.com'])
fp_report = tech_fp.generate_fingerprint_report(fingerprints)
```

## Configuration

Add to `config.yaml`:

```yaml
# Cloud Recon Configuration
cloud_recon:
  enabled: true
  output_dir: ./cloud_recon_data
  base_url: https://kaeferjaeger.gay/?dir=sni-ip-ranges
  providers:
    - amazon
    - digitalocean
    - google
    - microsoft
    - oracle
  ai_analysis:
    enabled: true
    high_value_keywords:
      - admin
      - api
      - auth
      - console
      - dashboard
      - payment
      - billing
      - account
      - user
      - data
      - cdn
      - cloud
      - storage
      - database
      - cache
  risk_threshold: 5

# Threat Intelligence API Keys
shodan_api_key: ${SHODAN_API_KEY:-}
censys_api_id: ${CENSYS_API_ID:-}
censys_api_secret: ${CENSYS_API_SECRET:-}
```

## Architecture

```
Enhanced Cloud Recon
├── CloudRecon (base)
│   ├── Download SNI data from kaeferjaeger.gay
│   ├── Process domains (Jason Haddix workflow)
│   └── Export for BountyCatch
├── IPAnalyzer
│   ├── Resolve domains to IPs
│   ├── ASN lookup
│   ├── Cloud provider detection
│   └── Geolocation
├── PortScanner
│   ├── Multi-port scanning
│   ├── Service identification
│   ├── Banner grabbing
│   └── Service categorization
├── SSLAnalyzer
│   ├── Certificate extraction
│   ├── Expiration tracking
│   ├── Wildcard detection
│   └── Security analysis
├── TechFingerprinter
│   ├── HTTP header analysis
│   ├── Technology detection
│   ├── CDN identification
│   └── Cloud infrastructure detection
├── ThreatIntelClient
│   ├── Shodan integration
│   ├── Censys integration
│   ├── Vulnerability tracking
│   └── Risk scoring
└── EnhancedCloudRecon
    ├── Orchestrates all modules
    ├── Historical tracking
    ├── Change detection
    └── Comprehensive reporting
```

## Use Cases

### Bug Bounty Research

1. **Target Discovery**
   ```bash
   python3 run_cloud_recon.py --enhanced --apex target.com
   ```
   - Find all cloud assets for target.com
   - Identify subdomains and IPs
   - Discover services and technologies

2. **Vulnerability Assessment**
   ```bash
   python3 run_cloud_recon.py --enhanced --threat-intel --apex target.com
   ```
   - Scan for open ports
   - Check for known vulnerabilities (Shodan/Censys)
   - Identify high-risk services

3. **Subdomain Takeover**
   ```bash
   python3 run_cloud_recon.py --enhanced --no-port --no-ssl --apex target.com
   ```
   - Focus on IP analysis and tech fingerprinting
   - Find CNAMEs pointing to cloud services
   - Identify takeover opportunities

### Security Assessments

1. **Infrastructure Mapping**
   ```bash
   python3 run_cloud_recon.py --enhanced --apex company.com
   ```
   - Map entire cloud infrastructure
   - Identify all cloud providers used
   - Document technology stack

2. **Certificate Management**
   ```bash
   python3 run_cloud_recon.py --enhanced --no-port --no-tech --apex company.com
   ```
   - Audit SSL certificates
   - Find expiring certificates
   - Identify self-signed certs

3. **Continuous Monitoring**
   ```python
   from cloud_recon import EnhancedCloudRecon

   recon = EnhancedCloudRecon()
   results = recon.run_killer_recon(apex_domain='company.com')
   
   # Compare with previous scan
   comparison = recon.compare_with_history('company_recon', days=7)
   print(comparison['changes'])
   ```

## Performance Considerations

### Parallel Processing
- IP resolution: 50 concurrent threads
- Port scanning: 10 concurrent threads (to avoid overwhelming targets)
- SSL analysis: 20 concurrent threads
- Tech fingerprinting: 20 concurrent threads

### Rate Limiting
- **ipinfo.io**: 50,000 requests/month (free tier)
- **Shodan**: 1 request/second (free tier)
- **Censys**: Depends on plan

### Resource Usage
- Memory: ~500MB for 10,000 domains
- Disk: ~50MB per historical snapshot
- Network: Depends on number of domains and features enabled

## Best Practices

1. **Start Small**
   - Test with a single apex domain first
   - Disable heavy features (port scan, threat intel) initially
   - Enable features incrementally

2. **Respect Rate Limits**
   - Use threat intel sparingly
   - Cache results locally
   - Implement exponential backoff for APIs

3. **Filter Results**
   - Use apex domain filtering to reduce scope
   - Focus on high-value keywords
   - Prioritize by risk score

4. **Historical Tracking**
   - Run regular scans (daily/weekly)
   - Compare results to detect changes
   - Archive old data to save space

5. **Integration**
   - Export results for BountyCatch
   - Import into domain management tools
   - Feed into automated testing pipelines

## Troubleshooting

### Issue: "No domains found"
**Solution:** 
- Check if SNI data downloaded successfully
- Verify apex domain spelling
- Try without apex domain filter

### Issue: "Port scan takes too long"
**Solution:**
- Reduce number of IPs scanned (automatic limit: 100)
- Disable port scanning with `--no-port`
- Increase timeout in config

### Issue: "SSL analysis fails"
**Solution:**
- Domain may not use HTTPS
- Check firewall allows 443
- Try with HTTP instead

### Issue: "Threat intel returns no results"
**Solution:**
- Verify API keys are set
- Check API quota limits
- IP may not be indexed by Shodan/Censys

## Future Enhancements

Planned features for future releases:

1. **Advanced Correlation**
   - Correlate domains with bug bounty reports
   - Cross-reference with known vulnerabilities
   - Identify common patterns

2. **Visualization**
   - Web dashboard for results
   - Interactive maps of infrastructure
   - Timeline views of changes

3. **Automation**
   - Continuous monitoring mode
   - Alert system for new assets
   - Automated BountyCatch import

4. **Integration**
   - BBRF integration
   - Notification systems (Slack, Discord)
   - API for external tools

5. **AI Enhancement**
   - Predictive risk scoring
   - Anomaly detection
   - Automated vulnerability prioritization

## Comparison: Basic vs Enhanced

| Feature | Basic | Enhanced |
|---------|-------|----------|
| SNI Data Download | ✓ | ✓ |
| Domain Processing | ✓ | ✓ |
| BountyCatch Export | ✓ | ✓ |
| IP Resolution | ✗ | ✓ |
| ASN Lookup | ✗ | ✓ |
| Cloud Detection | ✗ | ✓ |
| Port Scanning | ✗ | ✓ |
| SSL Analysis | ✗ | ✓ |
| Tech Fingerprinting | ✗ | ✓ |
| Threat Intel | ✗ | ✓ |
| Historical Tracking | ✗ | ✓ |
| Change Detection | ✗ | ✓ |
| Comprehensive Reports | ✗ | ✓ |

## References

- [Jason Haddix's SNI Workflow](https://github.com/jasonhaddix)
- [Kaeferjaeger SNI-IP Ranges](https://kaeferjaeger.gay/?dir=sni-ip-ranges)
- [Shodan API](https://developer.shodan.io/api)
- [Censys API](https://search.censys.com/api)
- [ipinfo.io API](https://ipinfo.io/developers)

## License

MIT License - See LICENSE file for details.
