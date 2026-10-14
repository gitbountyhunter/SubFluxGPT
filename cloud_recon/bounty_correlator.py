"""
Bug Bounty Correlation Module for Cloud Recon
Correlates cloud assets with bug bounty reports for target prioritization.
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class CorrelationResult:
    """Result of correlating cloud assets with bug bounty reports."""
    domain: str
    matching_reports: List[Dict]
    confidence: float
    recommended_action: str
    priority: str  # high, medium, low


class BountyCorrelator:
    """Correlates cloud assets with bug bounty reports."""
    
    def __init__(self, bug_bounty_reports: List[Dict] = None):
        """
        Initialize Bounty Correlator.
        
        Args:
            bug_bounty_reports: List of bug bounty reports
        """
        self.bug_bounty_reports = bug_bounty_reports or []
        self.domain_to_reports = self._index_reports()
    
    def _index_reports(self) -> Dict[str, List[Dict]]:
        """
        Index bug bounty reports by domain.
        
        Returns:
            Dictionary mapping domains to report lists
        """
        index = {}
        
        for report in self.bug_bounty_reports:
            # Extract domains from report
            domains = set()
            
            # From program field
            if report.get('program'):
                domains.add(report['program'])
            
            # From raw content
            if report.get('raw_content'):
                # Simple domain extraction
                import re
                domain_pattern = re.compile(r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                domains.update(domain_pattern.findall(report['raw_content']))
            
            # Index by domain
            for domain in domains:
                if domain not in index:
                    index[domain] = []
                index[domain].append(report)
        
        return index
    
    def correlate_domain(self, domain: str, cloud_asset_data: Dict = None) -> CorrelationResult:
        """
        Correlate a domain with bug bounty reports.
        
        Args:
            domain: Domain to correlate
            cloud_asset_data: Additional cloud asset data
            
        Returns:
            CorrelationResult
        """
        # Find matching reports
        matching_reports = []
        
        # Exact match
        if domain in self.domain_to_reports:
            matching_reports.extend(self.domain_to_reports[domain])
        
        # Subdomain match
        for indexed_domain, reports in self.domain_to_reports.items():
            if domain.endswith(indexed_domain) or indexed_domain.endswith(domain):
                matching_reports.extend(reports)
        
        # Deduplicate
        seen = set()
        unique_reports = []
        for report in matching_reports:
            report_id = report.get('id', report.get('title', ''))
            if report_id not in seen:
                seen.add(report_id)
                unique_reports.append(report)
        
        matching_reports = unique_reports
        
        # Calculate confidence
        confidence = 0.0
        if matching_reports:
            confidence = min(1.0, len(matching_reports) / 10.0)
        
        # Determine recommended action
        if len(matching_reports) > 5:
            recommended_action = "HIGH PRIORITY: Domain has extensive bug bounty history. Focus testing here."
            priority = "high"
        elif len(matching_reports) > 0:
            recommended_action = "MEDIUM PRIORITY: Domain has some bug bounty reports. Worth investigating."
            priority = "medium"
        else:
            recommended_action = "LOW PRIORITY: No bug bounty history. May be a new target."
            priority = "low"
        
        # Boost priority if cloud asset data indicates sensitive services
        if cloud_asset_data:
            if cloud_asset_data.get('has_database', False):
                priority = "high"
                recommended_action = "HIGH PRIORITY: Database detected. Critical asset."
                confidence += 0.2
            if cloud_asset_data.get('has_auth', False):
                priority = "high"
                recommended_action = "HIGH PRIORITY: Authentication service detected. Critical asset."
                confidence += 0.2
        
        return CorrelationResult(
            domain=domain,
            matching_reports=matching_reports,
            confidence=min(1.0, confidence),
            recommended_action=recommended_action,
            priority=priority
        )
    
    def correlate_assets(
        self,
        cloud_assets: Dict[str, List],
        cloud_data: Dict[str, Dict] = None
    ) -> Dict[str, CorrelationResult]:
        """
        Correlate multiple cloud assets with bug bounty reports.
        
        Args:
            cloud_assets: Cloud assets by provider (IPInfo objects)
            cloud_data: Additional cloud data by IP
            
        Returns:
            Dictionary mapping domains to CorrelationResult
        """
        results = {}
        
        # Extract domains from cloud assets
        all_domains = set()
        for provider, assets in cloud_assets.items():
            for asset in assets:
                if asset.domain:
                    all_domains.add(asset.domain)
        
        # Correlate each domain
        for domain in all_domains:
            asset_data = cloud_data.get(domain, {}) if cloud_data else {}
            results[domain] = self.correlate_domain(domain, asset_data)
        
        return results
    
    def prioritize_targets(
        self,
        correlation_results: Dict[str, CorrelationResult]
    ) -> List[Dict]:
        """
        Prioritize targets based on correlation results.
        
        Args:
            correlation_results: Correlation results by domain
            
        Returns:
            Sorted list of prioritized targets
        """
        prioritized = []
        
        for domain, result in correlation_results.items():
            prioritized.append({
                'domain': domain,
                'priority': result.priority,
                'confidence': result.confidence,
                'report_count': len(result.matching_reports),
                'recommended_action': result.recommended_action
            })
        
        # Sort by priority (high > medium > low) and confidence
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        prioritized.sort(key=lambda x: (priority_order[x['priority']], -x['confidence']))
        
        return prioritized
    
    def generate_correlation_report(
        self,
        correlation_results: Dict[str, CorrelationResult]
    ) -> Dict:
        """
        Generate a correlation report.
        
        Args:
            correlation_results: Correlation results by domain
            
        Returns:
            Report dictionary
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {},
            'by_priority': {'high': [], 'medium': [], 'low': []},
            'top_domains': []
        }
        
        # Categorize by priority
        for domain, result in correlation_results.items():
            report['by_priority'][result.priority].append({
                'domain': domain,
                'confidence': result.confidence,
                'report_count': len(result.matching_reports),
                'recommended_action': result.recommended_action
            })
        
        # Get prioritized list
        prioritized = self.prioritize_targets(correlation_results)
        report['top_domains'] = prioritized[:20]  # Top 20
        
        # Summary
        report['summary'] = {
            'total_domains': len(correlation_results),
            'high_priority': len(report['by_priority']['high']),
            'medium_priority': len(report['by_priority']['medium']),
            'low_priority': len(report['by_priority']['low']),
            'domains_with_reports': sum(1 for r in correlation_results.values() if r.matching_reports)
        }
        
        return report


def main():
    """Test Bounty Correlator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Correlate cloud assets with bug bounty reports")
    parser.add_argument('--domains', type=str, nargs='+', help='Domains to correlate')
    parser.add_argument('--file', type=str, help='File containing domains (one per line)')
    parser.add_argument('--reports', type=str, help='JSON file with bug bounty reports')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load reports if provided
    reports = []
    if args.reports:
        with open(args.reports, 'r') as f:
            reports = json.load(f)
    
    correlator = BountyCorrelator(reports)
    
    # Get domains
    if args.file:
        with open(args.file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    elif args.domains:
        domains = args.domains
    else:
        # Test with sample domains
        domains = ['google.com', 'amazon.com', 'example.com']
    
    # Correlate
    correlation_results = {}
    for domain in domains:
        correlation_results[domain] = correlator.correlate_domain(domain)
    
    report = correlator.generate_correlation_report(correlation_results)
    
    # Print report
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
