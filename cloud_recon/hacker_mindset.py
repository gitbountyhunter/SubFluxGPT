"""
Hacker Mindset Module for Cloud Recon
Advanced techniques and edge cases for bug bounty hunters.
"""

import logging
import re
import dns.resolver
import requests
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import concurrent.futures

logger = logging.getLogger(__name__)


@dataclass
class HackerFinding:
    """A potential vulnerability or attack surface."""
    type: str
    target: str
    description: str
    severity: str  # critical, high, medium, low, info
    confidence: float
    exploit_path: str
    poc_available: bool = False


class HackerMindset:
    """
    Hacker-focused analysis for cloud recon.
    Focuses on attack surfaces, vulnerabilities, and creative exploitation paths.
    """
    
    # Common takeover indicators
    TAKEOVER_PATTERNS = {
        'aws_s3': r'[a-z0-9-]+\.s3-website-[a-z0-9-]+\.amazonaws\.com',
        'azure': r'[a-z0-9-]+\.azurewebsites\.net',
        'heroku': r'[a-z0-9-]+\.herokuapp\.com',
        'github': r'[a-z0-9-]+\.github\.io',
        'cloudfront': r'[a-z0-9-]+\.cloudfront\.net',
        'fastly': r'[a-z0-9-]+\.fastly\.net',
        'cloudflare': r'[a-z0-9-]+\.pages\.dev',
        'vercel': r'[a-z0-9-]+\.vercel\.app',
        'netlify': r'[a-z0-9-]+\.netlify\.app',
    }
    
    # Sensitive keywords in domains
    SENSITIVE_KEYWORDS = [
        'admin', 'administrator', 'api', 'auth', 'authentication',
        'backup', 'billing', 'console', 'dashboard', 'database',
        'debug', 'dev', 'development', 'docs', 'internal', 'jenkins',
        'key', 'logs', 'mail', 'monitoring', 'preprod', 'private',
        'production', 'secret', 'staging', 'stats', 'test', 'testing',
        'uat', 'user', 'vpn', 'webhook', 'www', 'cms', 'portal',
        'gateway', 'proxy', 'server', 'client', 'service', 'worker'
    ]
    
    # High-value subdomain patterns
    HIGH_VALUE_PATTERNS = [
        r'api-[a-z0-9-]+',  # API versioning
        r'[a-z0-9-]+-api',  # API endpoints
        r'[a-z0-9-]+-admin',  # Admin panels
        r'admin-[a-z0-9-]+',  # Admin panels
        r'[a-z0-9-]+-staging',  # Staging environments
        r'[a-z0-9-]+-dev',  # Dev environments
        r'[a-z0-9-]+-test',  # Test environments
        r'[a-z0-9-]+-internal',  # Internal systems
        r'[a-z0-9-]+-private',  # Private systems
        r'[a-z0-9-]+-prod',  # Production systems
        r'[a-z0-9-]+-beta',  # Beta environments
        r'[a-z0-9-]+-backup',  # Backup systems
        r'[a-z0-9-]+-old',  # Deprecated systems
        r'[a-z0-9-]+-legacy',  # Legacy systems
    ]
    
    def __init__(self):
        """Initialize Hacker Mindset analyzer."""
        self.findings = []
    
    def detect_takeover_opportunities(self, domains: List[str]) -> List[HackerFinding]:
        """
        Detect potential subdomain takeover opportunities.
        
        Args:
            domains: List of domains to analyze
            
        Returns:
            List of HackerFinding for takeover opportunities
        """
        findings = []
        
        for domain in domains:
            for service, pattern in self.TAKEOVER_PATTERNS.items():
                if re.search(pattern, domain, re.IGNORECASE):
                    findings.append(HackerFinding(
                        type='subdomain_takeover',
                        target=domain,
                        description=f"Potential {service} subdomain takeover",
                        severity='high',
                        confidence=0.7,
                        exploit_path=f"Register {service} domain and verify DNS delegation",
                        poc_available=False
                    ))
        
        logger.info(f"Found {len(findings)} potential takeover opportunities")
        return findings
    
    def find_sensitive_subdomains(self, domains: List[str]) -> List[HackerFinding]:
        """
        Find subdomains with sensitive keywords.
        
        Args:
            domains: List of domains to analyze
            
        Returns:
            List of HackerFinding for sensitive subdomains
        """
        findings = []
        
        for domain in domains:
            domain_lower = domain.lower()
            
            for keyword in self.SENSITIVE_KEYWORDS:
                if keyword in domain_lower:
                    severity = 'high' if keyword in ['admin', 'api', 'auth', 'secret', 'key'] else 'medium'
                    
                    findings.append(HackerFinding(
                        type='sensitive_subdomain',
                        target=domain,
                        description=f"Sensitive keyword '{keyword}' in domain",
                        severity=severity,
                        confidence=0.8,
                        exploit_path=f"Test {keyword} functionality for authentication bypass, IDOR, or misconfigurations",
                        poc_available=False
                    ))
        
        logger.info(f"Found {len(findings)} sensitive subdomains")
        return findings
    
    def detect_versioned_environments(self, domains: List[str]) -> List[HackerFinding]:
        """
        Detect versioned environments (dev, staging, prod) that might have weaker security.
        
        Args:
            domains: List of domains to analyze
            
        Returns:
            List of HackerFinding for versioned environments
        """
        findings = []
        
        for domain in domains:
            domain_lower = domain.lower()
            
            if any(env in domain_lower for env in ['dev', 'staging', 'test', 'uat', 'preprod']):
                findings.append(HackerFinding(
                    type='versioned_environment',
                    target=domain,
                    description="Non-production environment detected - may have weaker security",
                    severity='medium',
                    confidence=0.6,
                    exploit_path="Test for development configurations, debug endpoints, weaker authentication",
                    poc_available=False
                ))
        
        logger.info(f"Found {len(findings)} versioned environments")
        return findings
    
    def check_dns_misconfigurations(self, domains: List[str]) -> List[HackerFinding]:
        """
        Check for DNS misconfigurations that could lead to vulnerabilities.
        
        Args:
            domains: List of domains to analyze
            
        Returns:
            List of HackerFinding for DNS misconfigurations
        """
        findings = []
        
        for domain in domains[:50]:  # Limit to avoid excessive DNS queries
            try:
                # Check for dangling CNAMEs
                answers = dns.resolver.resolve(domain, 'CNAME')
                for answer in answers:
                    target = str(answer.target).rstrip('.')
                    
                    # Check if target exists
                    try:
                        dns.resolver.resolve(target, 'A')
                    except:
                        findings.append(HackerFinding(
                            type='dangling_cname',
                            target=domain,
                            description=f"Dangling CNAME to {target} - potential takeover",
                            severity='high',
                            confidence=0.9,
                            exploit_path=f"Register {target} to claim {domain}",
                            poc_available=False
                        ))
                        
            except dns.resolver.NoAnswer:
                # No CNAME, check A record
                try:
                    dns.resolver.resolve(domain, 'A')
                except:
                    findings.append(HackerFinding(
                        type='dns_not_resolving',
                        target=domain,
                        description="Domain does not resolve - might be abandoned",
                        severity='low',
                        confidence=0.5,
                        exploit_path="Monitor for availability, attempt takeover if abandoned",
                        poc_available=False
                    ))
            except Exception as e:
                logger.debug(f"DNS check failed for {domain}: {e}")
        
        logger.info(f"Found {len(findings)} DNS misconfigurations")
        return findings
    
    def find_ignored_assets(self, domains: List[str], apex_domain: str) -> List[HackerFinding]:
        """
        Find assets that might be ignored or forgotten.
        
        Args:
            domains: List of domains to analyze
            apex_domain: Main apex domain
            
        Returns:
            List of HackerFinding for ignored assets
        """
        findings = []
        
        # Find subdomains with old or legacy patterns
        for domain in domains:
            domain_lower = domain.lower()
            
            if any(pattern in domain_lower for pattern in ['old', 'legacy', 'deprecated', 'archive', 'backup']):
                findings.append(HackerFinding(
                    type='ignored_asset',
                    target=domain,
                    description="Potentially ignored or forgotten asset",
                    severity='medium',
                    confidence=0.6,
                    exploit_path="Test for outdated software, weak configurations, or exposed data",
                    poc_available=False
                ))
        
        logger.info(f"Found {len(findings)} potentially ignored assets")
        return findings
    
    def check_http_vs_https(self, domains: List[str]) -> List[HackerFinding]:
        """
        Check for HTTP-only domains (missing HTTPS redirect).
        
        Args:
            domains: List of domains to analyze
            
        Returns:
            List of HackerFinding for HTTP-only domains
        """
        findings = []
        
        for domain in domains[:50]:  # Limit to avoid excessive HTTP requests
            try:
                # Try HTTP
                http_response = requests.get(f"http://{domain}", timeout=5, allow_redirects=False)
                
                # Try HTTPS
                try:
                    https_response = requests.get(f"https://{domain}", timeout=5, allow_redirects=False)
                    
                    # If HTTP works but HTTPS doesn't
                    if http_response.status_code < 400 and https_response.status_code >= 400:
                        findings.append(HackerFinding(
                            type='http_only',
                            target=domain,
                            description="HTTP accessible but HTTPS not available - potential MITM",
                            severity='medium',
                            confidence=0.7,
                            exploit_path="Test for sensitive data transmission over HTTP",
                            poc_available=False
                        ))
                        
                except:
                    # HTTPS fails, HTTP works
                    if http_response.status_code < 400:
                        findings.append(HackerFinding(
                            type='http_only',
                            target=domain,
                            description="HTTP accessible but HTTPS not available",
                            severity='medium',
                            confidence=0.7,
                            exploit_path="Test for sensitive data transmission over HTTP",
                            poc_available=False
                        ))
                        
            except Exception as e:
                logger.debug(f"HTTP/HTTPS check failed for {domain}: {e}")
        
        logger.info(f"Found {len(findings)} HTTP-only domains")
        return findings
    
    def generate_bounty_catch_remix_export(
        self,
        findings: List[HackerFinding],
        domains: List[str],
        apex_domain: str = None
    ) -> Dict:
        """
        Generate BountyCatch Remix compatible export.
        
        Args:
            findings: Hacker findings
            domains: All domains
            apex_domain: Apex domain
            
        Returns:
            BountyCatch Remix export data
        """
        # Categorize domains by priority
        critical_domains = []
        high_domains = []
        medium_domains = []
        low_domains = []
        
        # Add domains from findings
        for finding in findings:
            if finding.severity == 'critical':
                critical_domains.append(finding.target)
            elif finding.severity == 'high':
                high_domains.append(finding.target)
            elif finding.severity == 'medium':
                medium_domains.append(finding.target)
            else:
                low_domains.append(finding.target)
        
        # Add domains without findings (lower priority)
        finding_targets = set(f.target for f in findings)
        for domain in domains:
            if domain not in finding_targets:
                low_domains.append(domain)
        
        # Remove duplicates
        critical_domains = list(set(critical_domains))
        high_domains = list(set(high_domains))
        medium_domains = list(set(medium_domains))
        low_domains = list(set(low_domains))
        
        export = {
            'apex_domain': apex_domain,
            'timestamp': datetime.utcnow().isoformat(),
            'prioritized_lists': {
                'critical': critical_domains,
                'high': high_domains,
                'medium': medium_domains,
                'low': low_domains
            },
            'findings_summary': {
                'total_findings': len(findings),
                'by_type': {},
                'by_severity': {
                    'critical': len([f for f in findings if f.severity == 'critical']),
                    'high': len([f for f in findings if f.severity == 'high']),
                    'medium': len([f for f in findings if f.severity == 'medium']),
                    'low': len([f for f in findings if f.severity == 'low'])
                }
            },
            'bounty_catch_lists': {
                'high_priority': critical_domains + high_domains,
                'medium_priority': medium_domains,
                'low_priority': low_domains[:1000]  # Limit low priority
            }
        }
        
        # Count by type
        for finding in findings:
            if finding.type not in export['findings_summary']['by_type']:
                export['findings_summary']['by_type'][finding.type] = 0
            export['findings_summary']['by_type'][finding.type] += 1
        
        return export
    
    def run_hacker_analysis(
        self,
        domains: List[str],
        apex_domain: str = None,
        enable_dns_check: bool = True,
        enable_http_check: bool = True
    ) -> Dict:
        """
        Run complete hacker mindset analysis.
        
        Args:
            domains: List of domains to analyze
            apex_domain: Apex domain
            enable_dns_check: Enable DNS misconfiguration checks
            enable_http_check: Enable HTTP/HTTPS checks
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Running hacker mindset analysis on {len(domains)} domains")
        
        all_findings = []
        
        # Detect takeover opportunities
        takeover_findings = self.detect_takeover_opportunities(domains)
        all_findings.extend(takeover_findings)
        
        # Find sensitive subdomains
        sensitive_findings = self.find_sensitive_subdomains(domains)
        all_findings.extend(sensitive_findings)
        
        # Detect versioned environments
        versioned_findings = self.detect_versioned_environments(domains)
        all_findings.extend(versioned_findings)
        
        # Find ignored assets
        if apex_domain:
            ignored_findings = self.find_ignored_assets(domains, apex_domain)
            all_findings.extend(ignored_findings)
        
        # DNS misconfigurations
        if enable_dns_check:
            dns_findings = self.check_dns_misconfigurations(domains)
            all_findings.extend(dns_findings)
        
        # HTTP vs HTTPS
        if enable_http_check:
            http_findings = self.check_http_vs_https(domains)
            all_findings.extend(http_findings)
        
        # Generate BountyCatch Remix export
        bc_export = self.generate_bounty_catch_remix_export(all_findings, domains, apex_domain)
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'apex_domain': apex_domain,
            'total_domains_analyzed': len(domains),
            'total_findings': len(all_findings),
            'findings': all_findings,
            'bounty_catch_export': bc_export
        }
        
        logger.info(f"Hacker analysis complete: {len(all_findings)} findings")
        return results
    
    def export_for_bounty_catch(self, results: Dict, output_dir: str = './cloud_recon_data') -> str:
        """
        Export results in BountyCatch Remix format.
        
        Args:
            results: Analysis results
            output_dir: Output directory
            
        Returns:
            Path to exported file
        """
        from pathlib import Path
        
        output_path = Path(output_dir) / 'bountycatch'
        output_path.mkdir(parents=True, exist_ok=True)
        
        apex_domain = results.get('apex_domain', 'all_providers')
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Export high priority list
        high_priority_file = output_path / f"{apex_domain}_high_priority_{timestamp}.txt"
        with open(high_priority_file, 'w') as f:
            for domain in results['bounty_catch_export']['bounty_catch_lists']['high_priority']:
                f.write(f"{domain}\n")
        
        # Export medium priority list
        medium_priority_file = output_path / f"{apex_domain}_medium_priority_{timestamp}.txt"
        with open(medium_priority_file, 'w') as f:
            for domain in results['bounty_catch_export']['bounty_catch_lists']['medium_priority']:
                f.write(f"{domain}\n")
        
        # Export low priority list
        low_priority_file = output_path / f"{apex_domain}_low_priority_{timestamp}.txt"
        with open(low_priority_file, 'w') as f:
            for domain in results['bounty_catch_export']['bounty_catch_lists']['low_priority']:
                f.write(f"{domain}\n")
        
        # Export findings as JSON
        findings_file = output_path / f"{apex_domain}_findings_{timestamp}.json"
        import json
        with open(findings_file, 'w') as f:
            json.dump({
                'findings': [
                    {
                        'type': f.type,
                        'target': f.target,
                        'description': f.description,
                        'severity': f.severity,
                        'confidence': f.confidence,
                        'exploit_path': f.exploit_path
                    }
                    for f in results['findings']
                ]
            }, f, indent=2)
        
        logger.info(f"Exported for BountyCatch Remix to {output_path}")
        
        return str(output_path)


def main():
    """Test Hacker Mindset analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hacker mindset analysis for cloud recon")
    parser.add_argument('--domains', type=str, nargs='+', help='Domains to analyze')
    parser.add_argument('--file', type=str, help='File containing domains (one per line)')
    parser.add_argument('--apex', type=str, help='Apex domain')
    parser.add_argument('--no-dns', action='store_true', help='Disable DNS checks')
    parser.add_argument('--no-http', action='store_true', help='Disable HTTP checks')
    parser.add_argument('--export', action='store_true', help='Export for BountyCatch Remix')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    analyzer = HackerMindset()
    
    # Get domains
    if args.file:
        with open(args.file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    elif args.domains:
        domains = args.domains
    else:
        # Test with sample domains
        domains = ['api.example.com', 'admin.example.com', 'dev.example.com']
    
    # Run analysis
    results = analyzer.run_hacker_analysis(
        domains=domains,
        apex_domain=args.apex,
        enable_dns_check=not args.no_dns,
        enable_http_check=not args.no_http
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("HACKER MINDSET ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"\nTotal domains analyzed: {results['total_domains_analyzed']}")
    print(f"Total findings: {results['total_findings']}")
    
    print("\nFindings by severity:")
    severity_counts = results['bounty_catch_export']['findings_summary']['by_severity']
    for severity, count in severity_counts.items():
        print(f"  {severity}: {count}")
    
    print("\nFindings by type:")
    type_counts = results['bounty_catch_export']['findings_summary']['by_type']
    for finding_type, count in type_counts.items():
        print(f"  {finding_type}: {count}")
    
    # Export if requested
    if args.export:
        export_path = analyzer.export_for_bounty_catch(results)
        print(f"\nExported to: {export_path}")


if __name__ == '__main__':
    main()
