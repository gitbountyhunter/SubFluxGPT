"""
Technology Fingerprinting Module for Cloud Recon
Identifies technologies used by domains/ips (web servers, frameworks, etc.).
"""

import logging
import requests
import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


@dataclass
class TechInfo:
    """Information about detected technology."""
    ip: str
    domain: str
    technology: str
    category: str
    version: Optional[str] = None
    confidence: float = 1.0
    source: str = 'http_headers'


class TechFingerprinter:
    """Fingerprints technologies used by web services."""
    
    # Common technology signatures
    SIGNATURES = {
        'web_servers': {
            'nginx': {
                'header': 'Server',
                'pattern': r'nginx[/\s]*([\d.]+)?',
                'examples': ['nginx', 'nginx/1.18.0', 'nginx/1.21.6']
            },
            'apache': {
                'header': 'Server',
                'pattern': r'Apache[/\s]*([\d.]+)?',
                'examples': ['Apache', 'Apache/2.4.41', 'Apache/2.4.52']
            },
            'iis': {
                'header': 'Server',
                'pattern': r'IIS[/\s]*([\d.]+)?',
                'examples': ['IIS', 'IIS/10.0', 'Microsoft-IIS/10.0']
            },
            'cloudflare': {
                'header': 'Server',
                'pattern': r'cloudflare',
                'examples': ['cloudflare', 'cloudflare-nginx']
            },
            'gunicorn': {
                'header': 'Server',
                'pattern': r'gunicorn[/\s]*([\d.]+)?',
                'examples': ['gunicorn', 'gunicorn/20.1.0']
            },
            'caddy': {
                'header': 'Server',
                'pattern': r'Caddy',
                'examples': ['Caddy']
            }
        },
        'frameworks': {
            'django': {
                'header': 'X-Frame-Options',
                'pattern': r'SAMEORIGIN',
                'cookie': 'csrftoken'
            },
            'flask': {
                'header': 'Server',
                'pattern': r'Werkzeug'
            },
            'express': {
                'header': 'X-Powered-By',
                'pattern': r'Express'
            },
            'rails': {
                'header': 'X-Powered-By',
                'pattern': r'Phusion Passenger'
            },
            'laravel': {
                'header': 'X-Powered-By',
                'pattern': r'Laravel'
            }
        },
        'cdn': {
            'akamai': {
                'header': 'Server',
                'pattern': r'AkamaiGHost'
            },
            'fastly': {
                'header': 'Server',
                'pattern': r'Fastly'
            },
            'cloudfront': {
                'header': 'X-Amz-Cf-Id',
                'pattern': r'.+'
            },
            'cloudflare': {
                'header': 'cf-ray',
                'pattern': r'.+'
            }
        },
        'load_balancers': {
            'aws_elb': {
                'header': 'Server',
                'pattern': r'AWSELB'
            },
            'aws_alb': {
                'header': 'Server',
                'pattern': r'awselb'
            },
            'haproxy': {
                'header': 'Server',
                'pattern': r'HAProxy'
            },
            'nginx_lb': {
                'header': 'Server',
                'pattern': r'nginx'
            }
        }
    }
    
    def __init__(self, timeout: float = 5.0):
        """
        Initialize Tech Fingerprinter.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def get_http_headers(self, domain: str, port: int = 443, use_https: bool = True) -> Optional[Dict]:
        """
        Get HTTP headers from a domain.
        
        Args:
            domain: Domain name
            port: Port (default 443)
            use_https: Use HTTPS (default True)
            
        Returns:
            Dictionary of headers or None
        """
        try:
            protocol = 'https' if use_https else 'http'
            url = f"{protocol}://{domain}:{port}"
            
            response = requests.get(url, timeout=self.timeout, allow_redirects=False)
            return dict(response.headers)
            
        except Exception as e:
            logger.debug(f"Failed to get headers for {domain}: {e}")
            return None
    
    def analyze_headers(self, headers: Dict, domain: str, ip: str = None) -> List[TechInfo]:
        """
        Analyze HTTP headers to detect technologies.
        
        Args:
            headers: HTTP headers dictionary
            domain: Domain name
            ip: IP address (optional)
            
        Returns:
            List of detected technologies
        """
        technologies = []
        
        for category, techs in self.SIGNATURES.items():
            for tech_name, tech_info in techs.items():
                header_name = tech_info.get('header')
                pattern = tech_info.get('pattern')
                
                if header_name in headers:
                    header_value = headers[header_name]
                    
                    match = re.search(pattern, header_value, re.IGNORECASE)
                    if match:
                        version = match.group(1) if match.groups() else None
                        
                        technologies.append(TechInfo(
                            ip=ip or '',
                            domain=domain,
                            technology=tech_name,
                            category=category,
                            version=version,
                            source='http_headers'
                        ))
        
        return technologies
    
    def fingerprint_domain(self, domain: str, ip: str = None) -> List[TechInfo]:
        """
        Fingerprint technologies used by a domain.
        
        Args:
            domain: Domain name
            ip: IP address (optional)
            
        Returns:
            List of detected technologies
        """
        logger.info(f"Fingerprinting {domain}")
        
        # Try HTTPS first
        headers = self.get_http_headers(domain, 443, use_https=True)
        
        # Fallback to HTTP
        if not headers:
            headers = self.get_http_headers(domain, 80, use_https=False)
        
        if headers:
            technologies = self.analyze_headers(headers, domain, ip)
            logger.info(f"  Found {len(technologies)} technologies")
            return technologies
        
        return []
    
    def fingerprint_domains(self, domains: List[str]) -> Dict[str, List[TechInfo]]:
        """
        Fingerprint multiple domains in parallel.
        
        Args:
            domains: List of domains
            
        Returns:
            Dictionary mapping domains to technology lists
        """
        logger.info(f"Fingerprinting {len(domains)} domains")
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_domain = {
                executor.submit(self.fingerprint_domain, domain): domain
                for domain in domains
            }
            
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    technologies = future.result()
                    if technologies:
                        results[domain] = technologies
                except Exception as e:
                    logger.error(f"Error fingerprinting {domain}: {e}")
        
        logger.info(f"Fingerprinted {len(results)} domains")
        return results
    
    def categorize_technologies(self, fingerprint_results: Dict[str, List[TechInfo]]) -> Dict[str, List[Dict]]:
        """
        Categorize detected technologies.
        
        Args:
            fingerprint_results: Fingerprint results by domain
            
        Returns:
            Dictionary of technologies by category
        """
        categorized = {
            'web_servers': [],
            'frameworks': [],
            'cdn': [],
            'load_balancers': []
        }
        
        for domain, techs in fingerprint_results.items():
            for tech in techs:
                if tech.category in categorized:
                    categorized[tech.category].append({
                        'domain': domain,
                        'technology': tech.technology,
                        'version': tech.version
                    })
        
        return categorized
    
    def find_cloud_infrastructure(self, fingerprint_results: Dict[str, List[TechInfo]]) -> Dict[str, List[str]]:
        """
        Find domains using cloud infrastructure.
        
        Args:
            fingerprint_results: Fingerprint results by domain
            
        Returns:
            Dictionary mapping cloud providers to domain lists
        """
        cloud_infra = {
            'cloudflare': [],
            'aws': [],
            'gcp': [],
            'azure': []
        }
        
        for domain, techs in fingerprint_results.items():
            for tech in techs:
                if tech.technology == 'cloudflare':
                    cloud_infra['cloudflare'].append(domain)
                elif tech.technology == 'aws_elb' or tech.technology == 'aws_alb':
                    cloud_infra['aws'].append(domain)
                elif tech.technology == 'gunicorn':  # Often used on GCP
                    cloud_infra['gcp'].append(domain)
                elif tech.technology == 'iis':  # Often Azure
                    cloud_infra['azure'].append(domain)
        
        return cloud_infra
    
    def generate_fingerprint_report(self, fingerprint_results: Dict[str, List[TechInfo]]) -> Dict:
        """
        Generate a comprehensive fingerprint report.
        
        Args:
            fingerprint_results: Fingerprint results by domain
            
        Returns:
            Report dictionary
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {},
            'by_category': {},
            'cloud_infrastructure': {},
            'by_domain': {}
        }
        
        # By category
        report['by_category'] = self.categorize_technologies(fingerprint_results)
        
        # Cloud infrastructure
        report['cloud_infrastructure'] = self.find_cloud_infrastructure(fingerprint_results)
        
        # By domain
        for domain, techs in fingerprint_results.items():
            report['by_domain'][domain] = [
                {
                    'technology': tech.technology,
                    'category': tech.category,
                    'version': tech.version
                }
                for tech in techs
            ]
        
        # Summary
        total_domains = len(fingerprint_results)
        total_techs = sum(len(techs) for techs in fingerprint_results.values())
        
        report['summary'] = {
            'total_domains': total_domains,
            'total_detections': total_techs,
            'web_servers': len(report['by_category']['web_servers']),
            'frameworks': len(report['by_category']['frameworks']),
            'cdn': len(report['by_category']['cdn']),
            'load_balancers': len(report['by_category']['load_balancers']),
            'cloudflare_domains': len(report['cloud_infrastructure']['cloudflare']),
            'aws_domains': len(report['cloud_infrastructure']['aws'])
        }
        
        return report


def main():
    """Test Tech Fingerprinter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fingerprint technologies")
    parser.add_argument('--domains', type=str, nargs='+', help='Domains to analyze')
    parser.add_argument('--file', type=str, help='File containing domains (one per line)')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    fingerprinter = TechFingerprinter()
    
    # Get domains
    if args.file:
        with open(args.file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    elif args.domains:
        domains = args.domains
    else:
        # Test with sample domains
        domains = ['google.com', 'github.com', 'example.com']
    
    # Fingerprint
    results = fingerprinter.fingerprint_domains(domains)
    report = fingerprinter.generate_fingerprint_report(results)
    
    # Print report
    import json
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
