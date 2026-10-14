"""
Port Scanner Module for Cloud Recon
Scans IPs for open ports and services.
"""

import logging
import socket
import concurrent.futures
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import time

logger = logging.getLogger(__name__)


@dataclass
class PortResult:
    """Result of port scan."""
    ip: str
    port: int
    status: str  # open, closed, filtered
    service: Optional[str] = None
    banner: Optional[str] = None
    latency_ms: Optional[float] = None


class PortScanner:
    """Port scanner for cloud assets."""
    
    # Common ports to scan
    COMMON_PORTS = [
        21,    # FTP
        22,    # SSH
        23,    # Telnet
        25,    # SMTP
        53,    # DNS
        80,    # HTTP
        110,   # POP3
        143,   # IMAP
        443,   # HTTPS
        445,   # SMB
        993,   # IMAPS
        995,   # POP3S
        1433,  # MSSQL
        1521,  # Oracle
        3306,  # MySQL
        3389,  # RDP
        5432,  # PostgreSQL
        5900,  # VNC
        6379,  # Redis
        8080,  # HTTP-Alt
        8443,  # HTTPS-Alt
        9200,  # Elasticsearch
        27017, # MongoDB
    ]
    
    # Service mappings
    SERVICE_MAP = {
        21: 'ftp',
        22: 'ssh',
        23: 'telnet',
        25: 'smtp',
        53: 'dns',
        80: 'http',
        110: 'pop3',
        143: 'imap',
        443: 'https',
        445: 'smb',
        993: 'imaps',
        995: 'pop3s',
        1433: 'mssql',
        1521: 'oracle',
        3306: 'mysql',
        3389: 'rdp',
        5432: 'postgresql',
        5900: 'vnc',
        6379: 'redis',
        8080: 'http-alt',
        8443: 'https-alt',
        9200: 'elasticsearch',
        27017: 'mongodb',
    }
    
    def __init__(self, timeout: float = 2.0):
        """
        Initialize Port Scanner.
        
        Args:
            timeout: Connection timeout in seconds
        """
        self.timeout = timeout
    
    def scan_port(self, ip: str, port: int) -> PortResult:
        """
        Scan a single port on an IP.
        
        Args:
            ip: IP address
            port: Port number
            
        Returns:
            PortResult
        """
        start_time = time.time()
        result = PortResult(ip=ip, port=port, status='closed')
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            result = sock.connect_ex((ip, port))
            latency_ms = (time.time() - start_time) * 1000
            
            if result == 0:
                result.status = 'open'
                result.service = self.SERVICE_MAP.get(port, 'unknown')
                result.latency_ms = latency_ms
                
                # Try to grab banner
                try:
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    if banner:
                        result.banner = banner[:200]  # Limit banner length
                except:
                    pass
            else:
                result.status = 'closed'
                result.latency_ms = latency_ms
            
            sock.close()
            
        except socket.timeout:
            result.status = 'filtered'
            result.latency_ms = (time.time() - start_time) * 1000
        except Exception as e:
            logger.debug(f"Error scanning {ip}:{port}: {e}")
            result.status = 'error'
        
        return result
    
    def scan_ip(self, ip: str, ports: List[int] = None) -> List[PortResult]:
        """
        Scan multiple ports on an IP.
        
        Args:
            ip: IP address
            ports: List of ports to scan (default: COMMON_PORTS)
            
        Returns:
            List of PortResult
        """
        if ports is None:
            ports = self.COMMON_PORTS
        
        logger.info(f"Scanning {ip} on {len(ports)} ports")
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_port = {
                executor.submit(self.scan_port, ip, port): port
                for port in ports
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.status == 'open':
                        logger.info(f"  {ip}:{port} is OPEN ({result.service})")
                        
                except Exception as e:
                    logger.error(f"Error scanning port {port}: {e}")
        
        open_ports = [r for r in results if r.status == 'open']
        logger.info(f"Found {len(open_ports)} open ports on {ip}")
        
        return results
    
    def scan_ips(self, ips: List[str], ports: List[int] = None) -> Dict[str, List[PortResult]]:
        """
        Scan multiple IPs for open ports.
        
        Args:
            ips: List of IP addresses
            ports: List of ports to scan
            
        Returns:
            Dictionary mapping IPs to PortResult lists
        """
        if ports is None:
            ports = self.COMMON_PORTS
        
        logger.info(f"Scanning {len(ips)} IPs on {len(ports)} ports")
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ip = {
                executor.submit(self.scan_ip, ip, ports): ip
                for ip in ips
            }
            
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    results[ip] = future.result()
                except Exception as e:
                    logger.error(f"Error scanning {ip}: {e}")
                    results[ip] = []
        
        # Summary
        total_open = sum(len([r for r in results[ip] if r.status == 'open']) for ip in results)
        logger.info(f"Scan complete: {total_open} total open ports found")
        
        return results
    
    def find_interesting_services(self, scan_results: Dict[str, List[PortResult]]) -> Dict[str, List[Dict]]:
        """
        Find interesting services from scan results.
        
        Args:
            scan_results: Scan results by IP
            
        Returns:
            Dictionary of interesting services by category
        """
        interesting = {
            'databases': [],
            'remote_access': [],
            'web_services': [],
            'file_sharing': [],
            'email': []
        }
        
        database_ports = [1433, 1521, 3306, 5432, 6379, 27017, 9200]
        remote_access_ports = [22, 23, 3389, 5900]
        web_ports = [80, 443, 8080, 8443]
        file_sharing_ports = [21, 445]
        email_ports = [25, 110, 143, 993, 995]
        
        for ip, results in scan_results.items():
            for result in results:
                if result.status != 'open':
                    continue
                
                service_info = {
                    'ip': ip,
                    'port': result.port,
                    'service': result.service,
                    'banner': result.banner
                }
                
                if result.port in database_ports:
                    interesting['databases'].append(service_info)
                elif result.port in remote_access_ports:
                    interesting['remote_access'].append(service_info)
                elif result.port in web_ports:
                    interesting['web_services'].append(service_info)
                elif result.port in file_sharing_ports:
                    interesting['file_sharing'].append(service_info)
                elif result.port in email_ports:
                    interesting['email'].append(service_info)
        
        return interesting
    
    def generate_scan_report(self, scan_results: Dict[str, List[PortResult]]) -> Dict:
        """
        Generate a comprehensive scan report.
        
        Args:
            scan_results: Scan results by IP
            
        Returns:
            Report dictionary
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {},
            'by_ip': {},
            'by_port': {},
            'interesting_services': {}
        }
        
        # Analyze by IP
        for ip, results in scan_results.items():
            open_ports = [r for r in results if r.status == 'open']
            report['by_ip'][ip] = {
                'total_scanned': len(results),
                'open_ports': len(open_ports),
                'ports': [r.port for r in open_ports],
                'services': [r.service for r in open_ports if r.service]
            }
        
        # Analyze by port
        port_counts = {}
        for ip, results in scan_results.items():
            for result in results:
                if result.status == 'open':
                    port = result.port
                    if port not in port_counts:
                        port_counts[port] = 0
                    port_counts[port] += 1
        
        report['by_port'] = {
            port: {'count': count, 'service': self.SERVICE_MAP.get(port)}
            for port, count in port_counts.items()
        }
        
        # Summary
        total_ips = len(scan_results)
        total_open = sum(len([r for r in results if r.status == 'open']) for results in scan_results.values())
        
        report['summary'] = {
            'total_ips_scanned': total_ips,
            'total_open_ports': total_open,
            'unique_open_ports': len(port_counts),
            'avg_open_per_ip': total_open / total_ips if total_ips > 0 else 0
        }
        
        # Interesting services
        report['interesting_services'] = self.find_interesting_services(scan_results)
        
        return report


def main():
    """Test Port Scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan IPs for open ports")
    parser.add_argument('--ips', type=str, nargs='+', help='IPs to scan')
    parser.add_argument('--file', type=str, help='File containing IPs (one per line)')
    parser.add_argument('--ports', type=str, help='Comma-separated list of ports')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scanner = PortScanner()
    
    # Get IPs
    if args.file:
        with open(args.file, 'r') as f:
            ips = [line.strip() for line in f if line.strip()]
    elif args.ips:
        ips = args.ips
    else:
        # Test with localhost
        ips = ['127.0.0.1']
    
    # Get ports
    if args.ports:
        ports = [int(p.strip()) for p in args.ports.split(',')]
    else:
        ports = None
    
    # Scan
    results = scanner.scan_ips(ips, ports)
    report = scanner.generate_scan_report(results)
    
    # Print report
    import json
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
