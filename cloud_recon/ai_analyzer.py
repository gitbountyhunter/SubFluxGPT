"""
Cloud AI Analyzer Module
AI-powered analysis of cloud reconnaissance data.
"""

import logging
from typing import Dict, List, Optional, Set
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)


class CloudAIAnalyzer:
    """
    AI-powered analyzer for cloud reconnaissance data.
    Provides intelligent insights and recommendations.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Cloud AI Analyzer.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Known sensitive patterns
        self.sensitive_patterns = {
            'keys': ['key', 'secret', 'token', 'password', 'credential', 'auth'],
            'internal': ['internal', 'private', 'intranet', 'dev', 'staging', 'test'],
            'admin': ['admin', 'console', 'dashboard', 'panel', 'control'],
            'api': ['api', 'graphql', 'rest', 'soap', 'endpoint'],
            'data': ['db', 'database', 'storage', 'bucket', 'cache'],
            'auth': ['auth', 'login', 'oauth', 'sso', 'identity'],
        }

        # High-value targets
        self.high_value_keywords = [
            'admin', 'api', 'auth', 'console', 'dashboard',
            'payment', 'billing', 'account', 'user', 'data',
            'cdn', 'cloud', 'storage', 'database', 'cache'
        ]

    def analyze_cloud_assets(self, process_results: Dict) -> Dict:
        """
        Analyze processed cloud reconnaissance data with AI insights.

        Args:
            process_results: Results from CloudRecon processing

        Returns:
            AI analysis results
        """
        analysis = {
            'high_value_targets': [],
            'sensitive_domains': [],
            'pattern_analysis': {},
            'risk_assessment': {},
            'recommendations': [],
            'stats': {}
        }

        # Get all domains from combined results
        if 'combined' in process_results:
            all_domains = process_results['combined'].get('domains', [])
            all_wildcards = process_results['combined'].get('wildcards', [])
            all_apex = process_results['combined'].get('apex', [])
        else:
            # Aggregate from individual providers
            all_domains = []
            all_wildcards = []
            all_apex = []
            for provider, result in process_results.items():
                if isinstance(result, dict) and result.get('success'):
                    all_domains.extend(result.get('domains', []))
                    all_wildcards.extend(result.get('wildcards', []))
                    all_apex.extend(result.get('apex_domains', []))

        analysis['stats'] = {
            'total_domains': len(all_domains),
            'total_wildcards': len(all_wildcards),
            'total_apex': len(all_apex)
        }

        # Identify high-value targets
        analysis['high_value_targets'] = self._find_high_value_targets(all_domains)

        # Identify sensitive domains
        analysis['sensitive_domains'] = self._find_sensitive_domains(all_domains)

        # Pattern analysis
        analysis['pattern_analysis'] = self._analyze_patterns(all_domains)

        # Risk assessment
        analysis['risk_assessment'] = self._assess_risk(all_domains, all_wildcards)

        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def _find_high_value_targets(self, domains: List[str]) -> List[Dict]:
        """
        Find high-value target domains.

        Args:
            domains: List of domains

        Returns:
            List of high-value domain info
        """
        high_value = []

        for domain in domains:
            domain_lower = domain.lower()
            score = 0
            matched_keywords = []

            for keyword in self.high_value_keywords:
                if keyword in domain_lower:
                    score += 1
                    matched_keywords.append(keyword)

            if score >= 2:  # Domain matches 2+ high-value keywords
                high_value.append({
                    'domain': domain,
                    'score': score,
                    'keywords': matched_keywords
                })

        # Sort by score
        high_value.sort(key=lambda x: x['score'], reverse=True)

        return high_value[:50]  # Top 50

    def _find_sensitive_domains(self, domains: List[str]) -> List[Dict]:
        """
        Find potentially sensitive domains.

        Args:
            domains: List of domains

        Returns:
            List of sensitive domain info
        """
        sensitive = []

        for domain in domains:
            domain_lower = domain.lower()
            sensitivity_level = 0
            categories = []

            for category, keywords in self.sensitive_patterns.items():
                for keyword in keywords:
                    if keyword in domain_lower:
                        sensitivity_level += 1
                        categories.append(category)

            if sensitivity_level >= 1:
                sensitive.append({
                    'domain': domain,
                    'level': sensitivity_level,
                    'categories': list(set(categories))
                })

        # Sort by sensitivity level
        sensitive.sort(key=lambda x: x['level'], reverse=True)

        return sensitive[:50]

    def _analyze_patterns(self, domains: List[str]) -> Dict:
        """
        Analyze patterns in domains.

        Args:
            domains: List of domains

        Returns:
            Pattern analysis results
        """
        patterns = {
            'subdomain_depth': {},
            'common_prefixes': Counter(),
            'common_suffixes': Counter(),
            'tld_distribution': Counter(),
            'length_distribution': Counter()
        }

        for domain in domains:
            parts = domain.split('.')
            depth = len(parts) - 2

            # Depth distribution
            patterns['subdomain_depth'][depth] = patterns['subdomain_depth'].get(depth, 0) + 1

            # Common prefixes (first subdomain part)
            if len(parts) > 2:
                prefix = parts[0]
                patterns['common_prefixes'][prefix] += 1

            # Common suffixes (last subdomain part before TLD)
            if len(parts) > 2:
                suffix = parts[-2]
                patterns['common_suffixes'][suffix] += 1

            # TLD distribution
            tld = parts[-1]
            patterns['tld_distribution'][tld] += 1

            # Length distribution
            length = len(domain)
            patterns['length_distribution'][length] += 1

        # Convert counters to top 10
        patterns['common_prefixes'] = dict(patterns['common_prefixes'].most_common(10))
        patterns['common_suffixes'] = dict(patterns['common_suffixes'].most_common(10))
        patterns['tld_distribution'] = dict(patterns['tld_distribution'].most_common(10))
        patterns['length_distribution'] = dict(patterns['length_distribution'].most_common(10))

        return patterns

    def _assess_risk(self, domains: List[str], wildcards: List[str]) -> Dict:
        """
        Assess risk level of the reconnaissance data.

        Args:
            domains: List of regular domains
            wildcards: List of wildcard domains

        Returns:
            Risk assessment
        """
        risk_score = 0
        risk_factors = []

        # Factor 1: High number of domains
        if len(domains) > 10000:
            risk_score += 3
            risk_factors.append("Large attack surface (>10K domains)")
        elif len(domains) > 1000:
            risk_score += 2
            risk_factors.append("Medium attack surface (>1K domains)")

        # Factor 2: High number of wildcards
        if len(wildcards) > 1000:
            risk_score += 2
            risk_factors.append("Many wildcard patterns (>1K)")

        # Factor 3: Sensitive domains
        sensitive_count = sum(1 for d in domains if any(k in d.lower() for k in self.sensitive_patterns['keys']))
        if sensitive_count > 100:
            risk_score += 3
            risk_factors.append("Many potentially sensitive domains")
        elif sensitive_count > 10:
            risk_score += 1
            risk_factors.append("Some potentially sensitive domains")

        # Factor 4: High-value targets
        high_value_count = sum(1 for d in domains if any(k in d.lower() for k in self.high_value_keywords))
        if high_value_count > 500:
            risk_score += 2
            risk_factors.append("Many high-value targets")

        # Determine risk level
        if risk_score >= 8:
            risk_level = "CRITICAL"
        elif risk_score >= 5:
            risk_level = "HIGH"
        elif risk_score >= 3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            'score': risk_score,
            'level': risk_level,
            'factors': risk_factors
        }

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """
        Generate recommendations based on analysis.

        Args:
            analysis: Analysis results

        Returns:
            List of recommendations
        """
        recommendations = []

        # Based on high-value targets
        if analysis['high_value_targets']:
            recommendations.append(
                f"Prioritize {len(analysis['high_value_targets'])} high-value targets for testing"
            )

        # Based on sensitive domains
        if analysis['sensitive_domains']:
            recommendations.append(
                f"Carefully test {len(analysis['sensitive_domains'])} potentially sensitive domains"
            )

        # Based on risk assessment
        risk_level = analysis['risk_assessment'].get('level', 'LOW')
        if risk_level in ['HIGH', 'CRITICAL']:
            recommendations.append(
                f"Risk level is {risk_level} - allocate additional testing resources"
            )

        # Based on patterns
        common_prefixes = analysis['pattern_analysis'].get('common_prefixes', {})
        if 'api' in common_prefixes:
            recommendations.append("High number of API endpoints - consider API testing tools")

        if 'admin' in common_prefixes:
            recommendations.append("Admin panel discovery - prioritize authentication testing")

        # General recommendations
        recommendations.append("Use subdomain enumeration on apex domains")
        recommendations.append("Run vulnerability scanning on high-value targets")
        recommendations.append("Check for takeovers on wildcard domains")

        return recommendations

    def suggest_test_order(self, domains: List[str]) -> List[str]:
        """
        Suggest optimal testing order for domains.

        Args:
            domains: List of domains

        Returns:
            Ordered list of domains to test
        """
        scored = []

        for domain in domains:
            domain_lower = domain.lower()
            score = 0

            # High-value keywords
            for keyword in self.high_value_keywords:
                if keyword in domain_lower:
                    score += 2

            # Sensitive keywords
            for category, keywords in self.sensitive_patterns.items():
                for keyword in keywords:
                    if keyword in domain_lower:
                        score += 1

            # Shorter domains (usually more important)
            if len(domain) < 20:
                score += 1

            # Apex domains
            if domain.count('.') == 1:
                score += 3

            scored.append((score, domain))

        # Sort by score (descending)
        scored.sort(key=lambda x: x[0], reverse=True)

        return [domain for score, domain in scored]
