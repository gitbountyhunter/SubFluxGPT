"""
Continuous Monitoring Module for Cloud Recon
Automates regular scanning and alerting for cloud asset changes.
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import schedule
import time

logger = logging.getLogger(__name__)


class ContinuousMonitor:
    """Continuous monitoring for cloud assets."""
    
    def __init__(self, config: Optional[Dict] = None, config_path: str = 'config.yaml'):
        """
        Initialize Continuous Monitor.
        
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
        
        # Initialize enhanced cloud recon
        from .enhanced_cloud_recon import EnhancedCloudRecon
        self.recon = EnhancedCloudRecon(self.config, config_path)
        
        # Monitoring settings
        self.apex_domains = cloud_config.get('monitor_apex_domains', [])
        self.scan_interval_hours = cloud_config.get('scan_interval_hours', 24)
        self.alert_on_new_assets = cloud_config.get('alert_on_new_assets', True)
        self.alert_on_removed_assets = cloud_config.get('alert_on_removed_assets', True)
        
        # Alert settings
        self.alert_methods = cloud_config.get('alert_methods', ['log'])
        self.slack_webhook = self.config.get('slack_webhook')
        self.discord_webhook = self.config.get('discord_webhook')
        
        # Output directory
        self.output_dir = Path(cloud_config.get('output_dir', './cloud_recon_data'))
        self.alerts_dir = self.output_dir / 'alerts'
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Continuous Monitor initialized")
    
    def run_scan(self, apex_domain: str = None) -> Dict:
        """
        Run a single scan.
        
        Args:
            apex_domain: Apex domain to scan
            
        Returns:
            Scan results
        """
        logger.info(f"Running scan for {apex_domain or 'all domains'}")
        
        project_name = f"continuous_monitor_{apex_domain.replace('.', '_')}" if apex_domain else "continuous_monitor_all"
        
        results = self.recon.run_killer_recon(
            apex_domain=apex_domain,
            project_name=project_name,
            enable_ip_analysis=True,
            enable_port_scan=True,
            enable_ssl_analysis=True,
            enable_tech_fingerprint=True,
            enable_threat_intel=False  # Disabled for continuous monitoring to save API quota
        )
        
        return results
    
    def compare_with_previous(self, current_results: Dict, apex_domain: str = None) -> Dict:
        """
        Compare current scan with previous scan.
        
        Args:
            current_results: Current scan results
            apex_domain: Apex domain
            
        Returns:
            Comparison results
        """
        project_name = f"continuous_monitor_{apex_domain.replace('.', '_')}" if apex_domain else "continuous_monitor_all"
        
        comparison = self.recon.compare_with_history(project_name, days=7)
        
        return comparison
    
    def generate_alert(self, comparison: Dict, apex_domain: str = None) -> Optional[Dict]:
        """
        Generate alert based on comparison.
        
        Args:
            comparison: Comparison results
            apex_domain: Apex domain
            
        Returns:
            Alert dictionary or None
        """
        changes = comparison.get('changes', {})
        domain_changes = changes.get('domains', {})
        
        new_domains = domain_changes.get('new', 0)
        removed_domains = domain_changes.get('removed', 0)
        
        alert = None
        
        if (self.alert_on_new_assets and new_domains > 0) or \
           (self.alert_on_removed_assets and removed_domains > 0):
            
            alert = {
                'timestamp': datetime.utcnow().isoformat(),
                'apex_domain': apex_domain,
                'severity': 'info',
                'type': 'asset_change',
                'new_domains': new_domains,
                'removed_domains': removed_domains,
                'new_domain_list': domain_changes.get('new_domains', [])[:10],
                'removed_domain_list': domain_changes.get('removed_domains', [])[:10],
                'message': f"Asset change detected for {apex_domain or 'all domains'}: {new_domains} new, {removed_domains} removed"
            }
        
        return alert
    
    def send_alert(self, alert: Dict):
        """
        Send alert via configured methods.
        
        Args:
            alert: Alert dictionary
        """
        logger.info(f"Sending alert: {alert['message']}")
        
        # Log alert
        if 'log' in self.alert_methods:
            self._log_alert(alert)
        
        # Slack
        if 'slack' in self.alert_methods and self.slack_webhook:
            self._send_slack_alert(alert)
        
        # Discord
        if 'discord' in self.alert_methods and self.discord_webhook:
            self._send_discord_alert(alert)
        
        # Save alert
        alert_file = self.alerts_dir / f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2)
    
    def _log_alert(self, alert: Dict):
        """Log alert to file."""
        logger.warning(f"ALERT: {alert['message']}")
    
    def _send_slack_alert(self, alert: Dict):
        """Send alert to Slack."""
        try:
            import requests
            
            payload = {
                'text': alert['message'],
                'attachments': [{
                    'color': 'warning' if alert['severity'] == 'info' else 'danger',
                    'fields': [
                        {'title': 'Severity', 'value': alert['severity']},
                        {'title': 'New Domains', 'value': str(alert['new_domains'])},
                        {'title': 'Removed Domains', 'value': str(alert['removed_domains'])}
                    ]
                }]
            }
            
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Slack alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_discord_alert(self, alert: Dict):
        """Send alert to Discord."""
        try:
            import requests
            
            embed = {
                'title': 'Cloud Asset Change Detected',
                'description': alert['message'],
                'color': 16776960 if alert['severity'] == 'info' else 16711680,
                'fields': [
                    {'name': 'Severity', 'value': alert['severity']},
                    {'name': 'New Domains', 'value': str(alert['new_domains'])},
                    {'name': 'Removed Domains', 'value': str(alert['removed_domains'])}
                ],
                'timestamp': alert['timestamp']
            }
            
            payload = {'embeds': [embed]}
            
            response = requests.post(self.discord_webhook, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Discord alert sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle."""
        logger.info("=" * 60)
        logger.info("Starting Monitoring Cycle")
        logger.info("=" * 60)
        
        for apex_domain in self.apex_domains:
            logger.info(f"\nMonitoring: {apex_domain}")
            
            # Run scan
            current_results = self.run_scan(apex_domain)
            
            # Compare with previous
            comparison = self.compare_with_previous(current_results, apex_domain)
            
            # Generate and send alert
            alert = self.generate_alert(comparison, apex_domain)
            if alert:
                self.send_alert(alert)
        
        logger.info("\nMonitoring cycle complete")
    
    def start_continuous_monitoring(self):
        """Start continuous monitoring loop."""
        logger.info(f"Starting continuous monitoring (interval: {self.scan_interval_hours} hours)")
        
        # Schedule monitoring
        schedule.every(self.scan_interval_hours).hours.do(self.run_monitoring_cycle)
        
        # Run initial scan
        self.run_monitoring_cycle()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_once(self):
        """Run monitoring once and exit."""
        self.run_monitoring_cycle()


def main():
    """Test Continuous Monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuous monitoring for cloud assets")
    parser.add_argument('--continuous', action='store_true', help='Run in continuous mode')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--config', type=str, default='config.yaml', help='Config file path')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    monitor = ContinuousMonitor(config_path=args.config)
    
    if args.continuous:
        monitor.start_continuous_monitoring()
    elif args.once:
        monitor.run_once()
    else:
        print("Please specify --continuous or --once")


if __name__ == '__main__':
    main()
