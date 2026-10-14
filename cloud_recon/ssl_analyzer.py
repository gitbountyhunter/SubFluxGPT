"""
SSL/TLS Certificate Analyzer for Cloud Recon
Analyzes SSL certificates for domains and IPs.
"""

import ssl
import socket
import logging
import concurrent.futures
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import OpenSSL
from OpenSSL import crypto

logger = logging.getLogger(__name__)


@dataclass
class CertificateInfo:
    """Information about an SSL certificate."""
    domain: str
    ip: str
    issuer: Optional[str] = None
    subject: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    days_until_expiry: Optional[int] = None
    is_expired: bool = False
    is_self_signed: bool = False
    signature_algorithm: Optional[str] = None
    key_size: Optional[int] = None
    version: Optional[str] = None
    serial_number: Optional[str] = None
    san_domains: Optional[List[str]] = None


class SSLAnalyzer:
    """Analyzes SSL/TLS certificates."""
    
    def __init__(self, timeout: float = 5.0):
        """
        Initialize SSL Analyzer.
        
        Args:
            timeout: Connection timeout in seconds
        """
        self.timeout = timeout
    
    def get_certificate(self, domain: str, port: int = 443) -> Optional[CertificateInfo]:
        """
        Get SSL certificate for a domain.
        
        Args:
            domain: Domain name
            port: Port (default 443)
            
        Returns:
            CertificateInfo or None
        """
        try:
            # Get IP
            ip = socket.gethostbyname(domain)
            
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connect and get certificate
            with socket.create_connection((domain, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    cert_pem = ssl.DER_cert_to_PEM_cert(cert_der)
                    
                    # Parse certificate
                    x509 = crypto.load_certificate(crypto.FILETYPE_PEM, cert_pem)
                    
                    # Extract information
                    subject = x509.get_subject()
                    issuer = x509.get_issuer()
                    
                    subject_str = ', '.join([f'{b[0]}={b[1]}' for b in subject.get_components()])
                    issuer_str = ', '.join([f'{b[0]}={b[1]}' for b in issuer.get_components()])
                    
                    # Validity
                    valid_from = datetime.strptime(
                        x509.get_notBefore().decode('ascii'),
                        '%Y%m%d%H%M%SZ'
                    )
                    valid_to = datetime.strptime(
                        x509.get_notAfter().decode('ascii'),
                        '%Y%m%d%H%M%SZ'
                    )
                    
                    days_until_expiry = (valid_to - datetime.utcnow()).days
                    is_expired = days_until_expiry < 0
                    
                    # Check if self-signed
                    is_self_signed = (subject_str == issuer_str)
                    
                    # Signature algorithm
                    sig_alg = x509.get_signature_algorithm().decode('ascii')
                    
                    # Key size
                    pub_key = x509.get_pubkey()
                    key_size = pub_key.bits()
                    
                    # Version
                    version = x509.get_version()
                    
                    # Serial number
                    serial = hex(x509.get_serial_number())[2:].upper()
                    
                    # SAN (Subject Alternative Names)
                    san_domains = []
                    try:
                        for i in range(x509.get_extension_count()):
                            ext = x509.get_extension(i)
                            if ext.get_short_name() == b'subjectAltName':
                                san_str = str(ext)
                                for item in san_str.split(','):
                                    if 'DNS:' in item:
                                        san_domains.append(item.split('DNS:')[1].strip())
                    except:
                        pass
                    
                    return CertificateInfo(
                        domain=domain,
                        ip=ip,
                        issuer=issuer_str,
                        subject=subject_str,
                        valid_from=valid_from.isoformat(),
                        valid_to=valid_to.isoformat(),
                        days_until_expiry=days_until_expiry,
                        is_expired=is_expired,
                        is_self_signed=is_self_signed,
                        signature_algorithm=sig_alg,
                        key_size=key_size,
                        version=str(version),
                        serial_number=serial,
                        san_domains=san_domains
                    )
                    
        except Exception as e:
            logger.warning(f"Failed to get certificate for {domain}: {e}")
            return None
    
    def analyze_certificates(self, domains: List[str]) -> Dict[str, CertificateInfo]:
        """
        Analyze certificates for multiple domains.
        
        Args:
            domains: List of domains
            
        Returns:
            Dictionary mapping domains to CertificateInfo
        """
        logger.info(f"Analyzing certificates for {len(domains)} domains")
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_domain = {
                executor.submit(self.get_certificate, domain): domain
                for domain in domains
            }
            
            for future in concurrent.futures.as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    cert_info = future.result()
                    if cert_info:
                        results[domain] = cert_info
                        logger.info(f"  {domain}: {cert_info.issuer}")
                except Exception as e:
                    logger.error(f"Error analyzing {domain}: {e}")
        
        logger.info(f"Analyzed {len(results)} certificates")
        return results
    
    def find_wildcard_certificates(self, certificates: Dict[str, CertificateInfo]) -> Dict[str, List[str]]:
        """
        Find domains with wildcard certificates.
        
        Args:
            certificates: Certificate information by domain
            
        Returns:
            Dictionary mapping wildcard domains to covered domains
        """
        wildcard_certs = {}
        
        for domain, cert in certificates.items():
            if cert.san_domains:
                for san in cert.san_domains:
                    if san.startswith('*.'):
                        wildcard = san
                        if wildcard not in wildcard_certs:
                            wildcard_certs[wildcard] = []
                        wildcard_certs[wildcard].append(domain)
        
        return wildcard_certs
    
    def find_expiring_soon(self, certificates: Dict[str, CertificateInfo], days: int = 30) -> List[str]:
        """
        Find certificates expiring soon.
        
        Args:
            certificates: Certificate information by domain
            days: Days threshold
            
        Returns:
            List of domains with expiring certificates
        """
        expiring = []
        
        for domain, cert in certificates.items():
            if cert.days_until_expiry and cert.days_until_expiry < days:
                expiring.append(domain)
        
        return expiring
    
    def find_self_signed(self, certificates: Dict[str, CertificateInfo]) -> List[str]:
        """
        Find self-signed certificates.
        
        Args:
            certificates: Certificate information by domain
            
        Returns:
            List of domains with self-signed certificates
        """
        self_signed = [domain for domain, cert in certificates.items() if cert.is_self_signed]
        return self_signed
    
    def generate_certificate_report(self, certificates: Dict[str, CertificateInfo]) -> Dict:
        """
        Generate a comprehensive certificate report.
        
        Args:
            certificates: Certificate information by domain
            
        Returns:
            Report dictionary
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {},
            'by_issuer': {},
            'warnings': {}
        }
        
        # Count by issuer
        issuer_counts = {}
        for cert in certificates.values():
            issuer = cert.issuer or 'Unknown'
            if issuer not in issuer_counts:
                issuer_counts[issuer] = 0
            issuer_counts[issuer] += 1
        
        report['by_issuer'] = issuer_counts
        
        # Warnings
        report['warnings'] = {
            'expiring_soon': self.find_expiring_soon(certificates, 30),
            'expired': self.find_expiring_soon(certificates, 0),
            'self_signed': self.find_self_signed(certificates),
            'wildcard_certs': self.find_wildcard_certificates(certificates)
        }
        
        # Summary
        report['summary'] = {
            'total_analyzed': len(certificates),
            'unique_issuers': len(issuer_counts),
            'expiring_soon': len(report['warnings']['expiring_soon']),
            'expired': len(report['warnings']['expired']),
            'self_signed': len(report['warnings']['self_signed']),
            'wildcard_certs': len(report['warnings']['wildcard_certs'])
        }
        
        return report


def main():
    """Test SSL Analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze SSL certificates")
    parser.add_argument('--domains', type=str, nargs='+', help='Domains to analyze')
    parser.add_argument('--file', type=str, help='File containing domains (one per line)')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    analyzer = SSLAnalyzer()
    
    # Get domains
    if args.file:
        with open(args.file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    elif args.domains:
        domains = args.domains
    else:
        # Test with sample domains
        domains = ['google.com', 'github.com', 'example.com']
    
    # Analyze
    certificates = analyzer.analyze_certificates(domains)
    report = analyzer.generate_certificate_report(certificates)
    
    # Print report
    import json
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
