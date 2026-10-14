"""
Enhanced Cloud Recon Manager
Integrates all cloud recon modules with killer features.
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import yaml

from .cloud_recon import CloudRecon, CloudReconManager
from .ip_analyzer import IPAnalyzer
from .port_scanner import PortScanner
from .ssl_analyzer import SSLAnalyzer
from .tech_fingerprint import TechFingerprinter
from .threat_intel import ThreatIntelClient
from .hacker_mindset import HackerMindset

logger = logging.getLogger(__name__)


class EnhancedCloudRecon:
    """
    Enhanced Cloud Recon with killer features:
    - IP resolution and ASN lookup
    - Port scanning
    - SSL/TLS certificate analysis
    - Technology fingerprinting
    - Threat intelligence integration
    - Historical tracking
    - Comprehensive reporting
    """
    
    def __init__(self, config: Optional[Dict] = None, config_path: str = 'config.yaml'):
        """
        Initialize Enhanced Cloud Recon.
        
        Args:
            config: Configuration dictionary
            config_path: Path to config file
        """
        # Load config
        if config is None and config_path:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        
        self.config = config or {}
        cloud_config = self.config.get('cloud_recon', {})
        
        # Initialize base cloud recon
        self.cloud_recon = CloudRecon(
            output_dir=cloud_config.get('output_dir', './cloud_recon_data')
        )
        
        # Initialize analyzers
        self.ip_analyzer = IPAnalyzer()
        self.port_scanner = PortScanner()
        self.ssl_analyzer = SSLAnalyzer()
        self.tech_fingerprinter = TechFingerprinter()
        
        # Initialize threat intel client
        self.threat_intel = ThreatIntelClient(
            shodan_api_key=self.config.get('shodan_api_key'),
            censys_api_id=self.config.get('censys_api_id'),
            censys_api_secret=self.config.get('censys_api_secret')
        )
        
        # Initialize hacker mindset analyzer
        self.hacker_mindset = HackerMindset()
        
        # Historical data directory
        self.history_dir = Path(cloud_config.get('output_dir', './cloud_recon_data')) / 'history'
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Enhanced Cloud Recon initialized")
    
    def run_killer_recon(
        self,
        apex_domain: Optional[str] = None,
        project_name: str = 'enhanced_cloud_recon',
        enable_ip_analysis: bool = True,
        enable_port_scan: bool = True,
        enable_ssl_analysis: bool = True,
        enable_tech_fingerprint: bool = True,
        enable_threat_intel: bool = False,
        enable_hacker_mindset: bool = True
    ) -> Dict:
        """
        Run the enhanced cloud recon workflow with all killer features.
        
        Args:
            apex_domain: Optional apex domain to filter
            project_name: Project name
            enable_ip_analysis: Enable IP resolution and ASN lookup
            enable_port_scan: Enable port scanning
            enable_ssl_analysis: Enable SSL certificate analysis
            enable_tech_fingerprint: Enable technology fingerprinting
            enable_threat_intel: Enable threat intelligence (requires API keys)
            
        Returns:
            Complete results dictionary
        """
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'project_name': project_name,
            'apex_domain': apex_domain,
            'features_enabled': {
                'ip_analysis': enable_ip_analysis,
                'port_scan': enable_port_scan,
                'ssl_analysis': enable_ssl_analysis,
                'tech_fingerprint': enable_tech_fingerprint,
                'threat_intel': enable_threat_intel
            },
            'steps': {}
        }
        
        # Step 1: Download and process SNI data
        logger.info("=" * 60)
        logger.info("Step 1: Downloading and processing SNI-IP range data")
        logger.info("=" * 60)
        
        download_results = self.cloud_recon.download_all_providers()
        process_results = self.cloud_recon.process_all_providers(
            apex_domain=apex_domain,
            keep_wildcards=True
        )
        
        results['steps']['sni_data'] = {
            'download': download_results,
            'processing': process_results
        }
        
        # Get all domains
        all_domains = process_results.get('combined', {}).get('domains', [])
        logger.info(f"Found {len(all_domains)} domains")
        
        if not all_domains:
            logger.warning("No domains found. Skipping analysis steps.")
            return results
        
        # Step 2: IP Analysis
        if enable_ip_analysis:
            logger.info("=" * 60)
            logger.info("Step 2: IP Resolution and ASN Lookup")
            logger.info("=" * 60)
            
            cloud_assets = self.ip_analyzer.find_cloud_assets(all_domains)
            ip_report = self.ip_analyzer.generate_ip_report(cloud_assets)
            
            results['steps']['ip_analysis'] = ip_report
            
            # Collect IPs for further analysis
            all_ips = list(ip_report.get('unique_ips', []))
            logger.info(f"Resolved {len(all_ips)} unique IPs")
        else:
            all_ips = []
        
        # Step 3: Port Scanning
        if enable_port_scan and all_ips:
            logger.info("=" * 60)
            logger.info("Step 3: Port Scanning")
            logger.info("=" * 60)
            
            # Limit to first 100 IPs to avoid excessive scanning
            scan_ips = all_ips[:100]
            logger.info(f"Scanning {len(scan_ips)} IPs (limited to prevent excessive scanning)")
            
            scan_results = self.port_scanner.scan_ips(scan_ips)
            scan_report = self.port_scanner.generate_scan_report(scan_results)
            
            results['steps']['port_scan'] = scan_report
        else:
            scan_results = {}
        
        # Step 4: SSL Certificate Analysis
        if enable_ssl_analysis:
            logger.info("=" * 60)
            logger.info("Step 4: SSL/TLS Certificate Analysis")
            logger.info("=" * 60)
            
            # Limit to first 100 domains
            ssl_domains = all_domains[:100]
            logger.info(f"Analyzing certificates for {len(ssl_domains)} domains")
            
            certificates = self.ssl_analyzer.analyze_certificates(ssl_domains)
            ssl_report = self.ssl_analyzer.generate_certificate_report(certificates)
            
            results['steps']['ssl_analysis'] = ssl_report
        else:
            certificates = {}
        
        # Step 5: Technology Fingerprinting
        if enable_tech_fingerprint:
            logger.info("=" * 60)
            logger.info("Step 5: Technology Fingerprinting")
            logger.info("=" * 60)
            
            # Limit to first 100 domains
            fp_domains = all_domains[:100]
            logger.info(f"Fingerprinting {len(fp_domains)} domains")
            
            fingerprints = self.tech_fingerprinter.fingerprint_domains(fp_domains)
            fp_report = self.tech_fingerprinter.generate_fingerprint_report(fingerprints)
            
            results['steps']['tech_fingerprint'] = fp_report
        else:
            fingerprints = {}
        
        # Step 6: Threat Intelligence
        if enable_threat_intel and all_ips:
            logger.info("=" * 60)
            logger.info("Step 6: Threat Intelligence")
            logger.info("=" * 60)
            
            # Limit to first 50 IPs to respect API limits
            threat_ips = all_ips[:50]
            logger.info(f"Querying threat intel for {len(threat_ips)} IPs")
            
            threat_results = self.threat_intel.scan_ips(threat_ips)
            threat_report = self.threat_intel.generate_threat_report(threat_results)
            
            results['steps']['threat_intel'] = threat_report
        else:
            threat_results = {}
        
        # Step 7: Save Historical Data
        logger.info("=" * 60)
        logger.info("Step 7: Saving Historical Data")
        logger.info("=" * 60)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        history_file = self.history_dir / f"{project_name}_{timestamp}.json"
        
        with open(history_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        results['history_file'] = str(history_file)
        logger.info(f"Saved results to {history_file}")
        
        # Step 8: Generate Summary Report
        logger.info("=" * 60)
        logger.info("Step 8: Generating Summary Report")
        logger.info("=" * 60)
        
        summary = self.generate_summary_report(results)
        results['summary'] = summary
        
        logger.info("=" * 60)
        logger.info("Enhanced Cloud Recon Complete")
        logger.info("=" * 60)
        logger.info(f"Total domains: {len(all_domains)}")
        logger.info(f"Unique IPs: {len(all_ips)}")
        logger.info(f"Open ports: {scan_results.get('summary', {}).get('total_open_ports', 0)}")
        logger.info(f"Certificates analyzed: {len(certificates)}")
        logger.info(f"Technologies detected: {fingerprints.get('summary', {}).get('total_detections', 0)}")
        
        return results
    
    def generate_summary_report(self, results: Dict) -> Dict:
        """
        Generate a summary report from all results.
        
        Args:
            results: Complete results dictionary
            
        Returns:
            Summary report
        """
        summary = {
            'project_name': results.get('project_name'),
            'timestamp': results.get('timestamp'),
            'apex_domain': results.get('apex_domain'),
            'key_findings': []
        }
        
        # SNI Data
        sni_data = results.get('steps', {}).get('sni_data', {}).get('processing', {})
        if sni_data:
            combined = sni_data.get('combined', {})
            summary['key_findings'].append({
                'category': 'SNI Data',
                'finding': f"Found {combined.get('stats', {}).get('total_domains', 0)} domains across {len(sni_data)} cloud providers"
            })
        
        # IP Analysis
        ip_analysis = results.get('steps', {}).get('ip_analysis', {})
        if ip_analysis:
            ip_summary = ip_analysis.get('summary', {})
            summary['key_findings'].append({
                'category': 'IP Analysis',
                'finding': f"Resolved {ip_summary.get('unique_ips', 0)} unique IPs from {ip_summary.get('total_providers', 0)} cloud providers"
            })
        
        # Port Scan
        port_scan = results.get('steps', {}).get('port_scan', {})
        if port_scan:
            port_summary = port_scan.get('summary', {})
            interesting = port_scan.get('interesting_services', {})
            summary['key_findings'].append({
                'category': 'Port Scanning',
                'finding': f"Found {port_summary.get('total_open_ports', 0)} open ports including {len(interesting.get('databases', []))} databases and {len(interesting.get('remote_access', []))} remote access services"
            })
        
        # SSL Analysis
        ssl_analysis = results.get('steps', {}).get('ssl_analysis', {})
        if ssl_analysis:
            ssl_summary = ssl_analysis.get('summary', {})
            warnings = ssl_analysis.get('warnings', {})
            summary['key_findings'].append({
                'category': 'SSL Certificates',
                'finding': f"Analyzed {ssl_summary.get('total_analyzed', 0)} certificates: {ssl_summary.get('expiring_soon', 0)} expiring soon, {ssl_summary.get('self_signed', 0)} self-signed"
            })
        
        # Tech Fingerprint
        tech_fp = results.get('steps', {}).get('tech_fingerprint', {})
        if tech_fp:
            tech_summary = tech_fp.get('summary', {})
            cloud_infra = tech_fp.get('cloud_infrastructure', {})
            summary['key_findings'].append({
                'category': 'Technology Fingerprinting',
                'finding': f"Detected {tech_summary.get('total_detections', 0)} technologies across {tech_summary.get('total_domains', 0)} domains, including {tech_summary.get('cloudflare_domains', 0)} on Cloudflare"
            })
        
        # Threat Intel
        threat_intel = results.get('steps', {}).get('threat_intel', {})
        if threat_intel:
            threat_summary = threat_intel.get('summary', {})
            summary['key_findings'].append({
                'category': 'Threat Intelligence',
                'finding': f"Scanned {threat_summary.get('total_ips_scanned', 0)} IPs: {threat_summary.get('high_risk_ips', 0)} high-risk, {threat_summary.get('total_vulnerabilities', 0)} total vulnerabilities"
            })
        
        return summary
    
    def compare_with_history(self, project_name: str, days: int = 7) -> Dict:
        """
        Compare current results with historical data.
        
        Args:
            project_name: Project name
            days: Number of days to look back
            
        Returns:
            Comparison report
        """
        # Find historical files
        history_files = sorted(self.history_dir.glob(f"{project_name}_*.json"))
        
        if len(history_files) < 2:
            return {'error': 'Not enough historical data for comparison'}
        
        # Load most recent and previous
        current_file = history_files[-1]
        previous_file = history_files[-2]
        
        with open(current_file, 'r') as f:
            current_data = json.load(f)
        
        with open(previous_file, 'r') as f:
            previous_data = json.load(f)
        
        # Compare
        comparison = {
            'current_timestamp': current_data.get('timestamp'),
            'previous_timestamp': previous_data.get('timestamp'),
            'changes': {}
        }
        
        # Compare domain counts
        current_domains = current_data.get('steps', {}).get('sni_data', {}).get('processing', {}).get('combined', {}).get('domains', [])
        previous_domains = previous_data.get('steps', {}).get('sni_data', {}).get('processing', {}).get('combined', {}).get('domains', [])
        
        new_domains = set(current_domains) - set(previous_domains)
        removed_domains = set(previous_domains) - set(current_domains)
        
        comparison['changes']['domains'] = {
            'total_current': len(current_domains),
            'total_previous': len(previous_domains),
            'new': len(new_domains),
            'removed': len(removed_domains),
            'new_domains': list(new_domains)[:10],  # Limit to 10
            'removed_domains': list(removed_domains)[:10]
        }
        
        return comparison


def main():
    """Test Enhanced Cloud Recon."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run enhanced cloud recon")
    parser.add_argument('--apex', type=str, help='Apex domain to filter')
    parser.add_argument('--project', type=str, default='enhanced_cloud_recon', help='Project name')
    parser.add_argument('--no-ip', action='store_true', help='Disable IP analysis')
    parser.add_argument('--no-port', action='store_true', help='Disable port scanning')
    parser.add_argument('--no-ssl', action='store_true', help='Disable SSL analysis')
    parser.add_argument('--no-tech', action='store_true', help='Disable tech fingerprinting')
    parser.add_argument('--threat-intel', action='store_true', help='Enable threat intelligence')
    parser.add_argument('--config', type=str, default='config.yaml', help='Config file path')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    recon = EnhancedCloudRecon(config_path=args.config)
    
    results = recon.run_killer_recon(
        apex_domain=args.apex,
        project_name=args.project,
        enable_ip_analysis=not args.no_ip,
        enable_port_scan=not args.no_port,
        enable_ssl_analysis=not args.no_ssl,
        enable_tech_fingerprint=not args.no_tech,
        enable_threat_intel=args.threat_intel
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for finding in results.get('summary', {}).get('key_findings', []):
        print(f"\n{finding['category']}:")
        print(f"  {finding['finding']}")
    
    print(f"\nFull results saved to: {results.get('history_file')}")


if __name__ == '__main__':
    main()
