"""
IP Analyzer Module for Cloud Recon
Resolves domains to IPs, performs ASN lookups, and analyzes IP ranges.
"""

import socket
import logging
import concurrent.futures
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import ipaddress
import requests

logger = logging.getLogger(__name__)


@dataclass
class IPInfo:
    """Information about an IP address."""
    ip: str
    domain: str
    asn: Optional[str] = None
    asn_name: Optional[str] = None
    country: Optional[str] = None
    provider: Optional[str] = None
    is_cloud: bool = False
    cloud_provider: Optional[str] = None


class IPAnalyzer:
    """Analyzes IP addresses and ranges for cloud assets."""
    
    # Cloud provider IP ranges (simplified)
    CLOUD_RANGES = {
        'AWS': [
            '3.0.0.0/8',
            '13.32.0.0/9',
            '52.0.0.0/10',
            '54.0.0.0/8',
            '100.24.0.0/12',
            '172.16.0.0/12',
        ],
        'Google': [
            '8.8.8.0/24',
            '35.190.0.0/16',
            '34.0.0.0/15',
            '66.102.0.0/20',
        ],
        'Azure': [
            '13.64.0.0/10',
            '20.0.0.0/8',
            '40.64.0.0/10',
            '52.96.0.0/14',
        ],
        'DigitalOcean': [
            '104.236.0.0/16',
            '143.198.0.0/16',
            '164.90.0.0/16',
        ],
        'Oracle': [
            '129.146.0.0/16',
            '132.226.0.0/16',
            '140.213.0.0/16',
        ]
    }
    
    def __init__(self):
        """Initialize IP Analyzer."""
        self.ip_cache = {}
        self.asn_cache = {}
    
    def resolve_domain(self, domain: str) -> List[str]:
        """
        Resolve a domain to IP addresses.
        
        Args:
            domain: Domain to resolve
            
        Returns:
            List of IP addresses
        """
        try:
            # Try IPv4
            result = socket.getaddrinfo(domain, None, socket.AF_INET)
            ips = list(set([addr[4][0] for addr in result]))
            return ips
        except socket.gaierror as e:
            logger.warning(f"Failed to resolve {domain}: {e}")
            return []
    
    def resolve_domains_parallel(self, domains: List[str], max_workers: int = 50) -> Dict[str, List[str]]:
        """
        Resolve multiple domains in parallel.
        
        Args:
            domains: List of domains to resolve
            max_workers: Number of parallel workers
            
        Returns:
            Dictionary mapping domains to IP lists
        """
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_domain = {
                executor.submit(self.resolve_domain, domain): domain
                for domain in domains
            }
            
            for future in concurrent.futures.as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    ips = future.result()
                    results[domain] = ips
                except Exception as e:
                    logger.error(f"Error resolving {domain}: {e}")
                    results[domain] = []
        
        logger.info(f"Resolved {len(results)} domains")
        return results
    
    def lookup_asn(self, ip: str) -> Optional[Dict]:
        """
        Look up ASN information for an IP using public APIs.
        
        Args:
            ip: IP address
            
        Returns:
            ASN information dictionary
        """
        if ip in self.asn_cache:
            return self.asn_cache[ip]
        
        try:
            # Use ipinfo.io (free tier: 50k requests/month)
            response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
            response.raise_for_status()
            data = response.json()
            
            asn_info = {
                'asn': data.get('org', '').split()[0] if data.get('org') else None,
                'asn_name': data.get('org'),
                'country': data.get('country'),
                'city': data.get('city'),
                'region': data.get('region'),
                'timezone': data.get('timezone')
            }
            
            self.asn_cache[ip] = asn_info
            return asn_info
            
        except Exception as e:
            logger.warning(f"ASN lookup failed for {ip}: {e}")
            return None
    
    def is_cloud_ip(self, ip: str) -> Tuple[bool, Optional[str]]:
        """
        Check if an IP belongs to a cloud provider.
        
        Args:
            ip: IP address
            
        Returns:
            Tuple of (is_cloud, cloud_provider)
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            for provider, ranges in self.CLOUD_RANGES.items():
                for range_str in ranges:
                    network = ipaddress.ip_network(range_str)
                    if ip_obj in network:
                        return True, provider
            
            return False, None
            
        except ValueError:
            return False, None
    
    def analyze_ip(self, ip: str, domain: str = None) -> IPInfo:
        """
        Perform comprehensive IP analysis.
        
        Args:
            ip: IP address
            domain: Source domain (optional)
            
        Returns:
            IPInfo object
        """
        is_cloud, cloud_provider = self.is_cloud_ip(ip)
        asn_info = self.lookup_asn(ip)
        
        return IPInfo(
            ip=ip,
            domain=domain or '',
            asn=asn_info.get('asn') if asn_info else None,
            asn_name=asn_info.get('asn_name') if asn_info else None,
            country=asn_info.get('country') if asn_info else None,
            provider=asn_info.get('asn_name') if asn_info else None,
            is_cloud=is_cloud,
            cloud_provider=cloud_provider
        )
    
    def analyze_ip_range(self, cidr: str) -> Dict:
        """
        Analyze an IP range.
        
        Args:
            cidr: CIDR notation (e.g., 192.168.1.0/24)
            
        Returns:
            Analysis results
        """
        try:
            network = ipaddress.ip_network(cidr)
            
            return {
                'cidr': cidr,
                'network_address': str(network.network_address),
                'broadcast_address': str(network.broadcast_address),
                'num_addresses': network.num_addresses,
                'version': network.version,
                'is_private': network.is_private,
                'is_multicast': network.is_multicast
            }
        except ValueError as e:
            logger.error(f"Invalid CIDR {cidr}: {e}")
            return {}
    
    def find_cloud_assets(self, domains: List[str]) -> Dict[str, List[IPInfo]]:
        """
        Find cloud assets among domains.
        
        Args:
            domains: List of domains to analyze
            
        Returns:
            Dictionary mapping cloud providers to IPInfo lists
        """
        logger.info(f"Analyzing {len(domains)} domains for cloud assets")
        
        # Resolve domains
        domain_to_ips = self.resolve_domains_parallel(domains)
        
        # Analyze IPs
        cloud_assets = {}
        
        for domain, ips in domain_to_ips.items():
            for ip in ips:
                info = self.analyze_ip(ip, domain)
                
                if info.is_cloud:
                    provider = info.cloud_provider
                    if provider not in cloud_assets:
                        cloud_assets[provider] = []
                    cloud_assets[provider].append(info)
        
        # Log summary
        for provider, assets in cloud_assets.items():
            logger.info(f"Found {len(assets)} {provider} assets")
        
        return cloud_assets
    
    def generate_ip_report(self, cloud_assets: Dict[str, List[IPInfo]]) -> Dict:
        """
        Generate a comprehensive IP analysis report.
        
        Args:
            cloud_assets: Cloud assets by provider
            
        Returns:
            Report dictionary
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {},
            'by_provider': {},
            'unique_ips': set(),
            'unique_asns': set(),
            'countries': set()
        }
        
        for provider, assets in cloud_assets.items():
            provider_report = {
                'count': len(assets),
                'unique_ips': len(set([a.ip for a in assets])),
                'domains': list(set([a.domain for a in assets if a.domain])),
                'asns': list(set([a.asn for a in assets if a.asn])),
                'countries': list(set([a.country for a in assets if a.country]))
            }
            
            report['by_provider'][provider] = provider_report
            report['unique_ips'].update([a.ip for a in assets])
            report['unique_asns'].update([a.asn for a in assets if a.asn])
            report['countries'].update([a.country for a in assets if a.country])
        
        report['summary'] = {
            'total_providers': len(cloud_assets),
            'total_assets': sum(len(assets) for assets in cloud_assets.values()),
            'unique_ips': len(report['unique_ips']),
            'unique_asns': len(report['unique_asns']),
            'countries': len(report['countries'])
        }
        
        # Convert sets to lists for JSON serialization
        report['unique_ips'] = list(report['unique_ips'])
        report['unique_asns'] = list(report['unique_asns'])
        report['countries'] = list(report['countries'])
        
        return report


def main():
    """Test IP Analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze IP addresses for cloud assets")
    parser.add_argument('--domains', type=str, nargs='+', help='Domains to analyze')
    parser.add_argument('--file', type=str, help='File containing domains (one per line)')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    analyzer = IPAnalyzer()
    
    # Get domains
    if args.file:
        with open(args.file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    elif args.domains:
        domains = args.domains
    else:
        # Test with sample domains
        domains = ['google.com', 'amazon.com', 'microsoft.com']
    
    # Analyze
    cloud_assets = analyzer.find_cloud_assets(domains)
    report = analyzer.generate_ip_report(cloud_assets)
    
    # Print report
    import json
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
