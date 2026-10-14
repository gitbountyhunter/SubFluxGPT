"""
Threat Intelligence Module for Cloud Recon
Integrates with Shodan, Censys, and other threat intel sources.
"""

import logging
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class ThreatIntel:
    """Threat intelligence information."""
    ip: str
    source: str
    vulnerabilities: List[str]
    services: List[str]
    ports: List[int]
    tags: List[str]
    last_seen: Optional[str] = None
    score: Optional[int] = None


class ThreatIntelClient:
    """Client for threat intelligence APIs."""
    
    def __init__(self, shodan_api_key: str = None, censys_api_id: str = None, censys_api_secret: str = None):
        """
        Initialize Threat Intel Client.
        
        Args:
            shodan_api_key: Shodan API key
            censys_api_id: Censys API ID
            censys_api_secret: Censys API secret
        """
        self.shodan_api_key = shodan_api_key
        self.censys_api_id = censys_api_id
        self.censys_api_secret = censys_api_secret
    
    def query_shodan(self, ip: str) -> Optional[Dict]:
        """
        Query Shodan for an IP.
        
        Args:
            ip: IP address
            
        Returns:
            Shodan data or None
        """
        if not self.shodan_api_key:
            logger.warning("Shodan API key not provided")
            return None
        
        try:
            url = f"https://api.shodan.io/shodan/host/{ip}?key={self.shodan_api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Shodan query failed for {ip}: {e}")
            return None
    
    def query_censys(self, ip: str) -> Optional[Dict]:
        """
        Query Censys for an IP.
        
        Args:
            ip: IP address
            
        Returns:
            Censys data or None
        """
        if not self.censys_api_id or not self.censys_api_secret:
            logger.warning("Censys API credentials not provided")
            return None
        
        try:
            url = f"https://search.censys.io/api/v2/hosts/{ip}"
            auth = (self.censys_api_id, self.censys_api_secret)
            response = requests.get(url, auth=auth, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Censys query failed for {ip}: {e}")
            return None
    
    def parse_shodan_data(self, data: Dict) -> ThreatIntel:
        """
        Parse Shodan response into ThreatIntel.
        
        Args:
            data: Shodan response data
            
        Returns:
            ThreatIntel object
        """
        ip = data.get('ip_str', '')
        
        # Extract vulnerabilities
        vulns = data.get('vulns', [])
        
        # Extract services
        services = []
        if 'ports' in data:
            services = [f"Port {port}" for port in data['ports']]
        
        # Extract tags
        tags = data.get('tags', [])
        
        # Extract ports
        ports = data.get('ports', [])
        
        # Last seen
        last_seen = data.get('last_update')
        
        # Calculate risk score (simple heuristic)
        score = 0
        if vulns:
            score += len(vulns) * 10
        if 22 in ports:  # SSH
            score += 5
        if 3389 in ports:  # RDP
            score += 10
        if 'malware' in tags:
            score += 50
        
        return ThreatIntel(
            ip=ip,
            source='shodan',
            vulnerabilities=vulns,
            services=services,
            ports=ports,
            tags=tags,
            last_seen=last_seen,
            score=score
        )
    
    def parse_censys_data(self, data: Dict) -> ThreatIntel:
        """
        Parse Censys response into ThreatIntel.
        
        Args:
            data: Censys response data
            
        Returns:
            ThreatIntel object
        """
        ip = data.get('ip', '')
        
        # Extract services
        services = []
        ports = []
        if 'services' in data:
            for service in data['services']:
                service_name = service.get('service_name', 'unknown')
                port = service.get('port')
                services.append(service_name)
                ports.append(port)
        
        # Extract vulnerabilities (Censys doesn't provide this directly)
        vulns = []
        
        # Extract tags
        tags = []
        if 'autonomous_system' in data:
            tags.append(data['autonomous_system'].get('asn', ''))
        
        # Last seen
        last_seen = data.get('last_at')
        
        return ThreatIntel(
            ip=ip,
            source='censys',
            vulnerabilities=vulns,
            services=services,
            ports=ports,
            tags=tags,
            last_seen=last_seen,
            score=None
        )
    
    def get_threat_intel(self, ip: str) -> List[ThreatIntel]:
        """
        Get threat intelligence from all available sources.
        
        Args:
            ip: IP address
            
        Returns:
            List of ThreatIntel objects
        """
        results = []
        
        # Try Shodan
        shodan_data = self.query_shodan(ip)
        if shodan_data:
            results.append(self.parse_shodan_data(shodan_data))
        
        # Try Censys
        censys_data = self.query_censys(ip)
        if censys_data:
            results.append(self.parse_censys_data(censys_data))
        
        return results
    
    def scan_ips(self, ips: List[str]) -> Dict[str, List[ThreatIntel]]:
        """
        Scan multiple IPs for threat intelligence.
        
        Args:
            ips: List of IP addresses
            
        Returns:
            Dictionary mapping IPs to ThreatIntel lists
        """
        logger.info(f"Scanning {len(ips)} IPs for threat intelligence")
        
        results = {}
        
        for ip in ips:
            intel = self.get_threat_intel(ip)
            if intel:
                results[ip] = intel
                logger.info(f"  {ip}: {len(intel)} sources")
        
        logger.info(f"Found threat intel for {len(results)} IPs")
        return results
    
    def generate_threat_report(self, threat_results: Dict[str, List[ThreatIntel]]) -> Dict:
        """
        Generate a threat intelligence report.
        
        Args:
            threat_results: Threat intel by IP
            
        Returns:
            Report dictionary
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {},
            'high_risk_ips': [],
            'vulnerabilities': {},
            'services': {},
            'by_source': {}
        }
        
        all_vulns = {}
        all_services = {}
        by_source = {'shodan': 0, 'censys': 0}
        
        for ip, intel_list in threat_results.items():
            for intel in intel_list:
                # Count by source
                by_source[intel.source] += 1
                
                # Collect vulnerabilities
                for vuln in intel.vulnerabilities:
                    if vuln not in all_vulns:
                        all_vulns[vuln] = 0
                    all_vulns[vuln] += 1
                
                # Collect services
                for service in intel.services:
                    if service not in all_services:
                        all_services[service] = 0
                    all_services[service] += 1
                
                # High risk IPs
                if intel.score and intel.score > 50:
                    report['high_risk_ips'].append({
                        'ip': ip,
                        'score': intel.score,
                        'vulnerabilities': len(intel.vulnerabilities),
                        'source': intel.source
                    })
        
        report['vulnerabilities'] = all_vulns
        report['services'] = all_services
        report['by_source'] = by_source
        
        # Summary
        report['summary'] = {
            'total_ips_scanned': len(threat_results),
            'ips_with_intel': len(threat_results),
            'high_risk_ips': len(report['high_risk_ips']),
            'total_vulnerabilities': sum(all_vulns.values()),
            'unique_vulnerabilities': len(all_vulns),
            'unique_services': len(all_services)
        }
        
        return report


def main():
    """Test Threat Intel Client."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Query threat intelligence APIs")
    parser.add_argument('--ips', type=str, nargs='+', help='IPs to query')
    parser.add_argument('--file', type=str, help='File containing IPs (one per line)')
    parser.add_argument('--shodan-key', type=str, help='Shodan API key')
    parser.add_argument('--censys-id', type=str, help='Censys API ID')
    parser.add_argument('--censys-secret', type=str, help='Censys API secret')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    client = ThreatIntelClient(
        shodan_api_key=args.shodan_key,
        censys_api_id=args.censys_id,
        censys_api_secret=args.censys_secret
    )
    
    # Get IPs
    if args.file:
        with open(args.file, 'r') as f:
            ips = [line.strip() for line in f if line.strip()]
    elif args.ips:
        ips = args.ips
    else:
        print("No IPs provided. Use --ips or --file")
        return
    
    # Scan
    results = client.scan_ips(ips)
    report = client.generate_threat_report(results)
    
    # Print report
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
