"""
AI-Powered Threat Intelligence Analyzer
Analyzes domains, IPs, and technologies for threat intelligence
Integrates with multiple threat feeds and uses AI for correlation
"""

import logging
import json
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import ipaddress

logger = logging.getLogger(__name__)


class ThreatIntelligenceAnalyzer:
    """AI-powered threat intelligence analyzer"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize threat intelligence analyzer

        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.threat_feeds = self._initialize_threat_feeds()
        self.local_cache = {}
        self.ai_analyzer = self._init_ai_analyzer()

    def _initialize_threat_feeds(self) -> Dict[str, Any]:
        """Initialize threat intelligence feeds"""
        return {
            'virustotal': {
                'enabled': self.config.get('virustotal', {}).get('enabled', False),
                'api_key': self.config.get('virustotal', {}).get('api_key', ''),
                'base_url': 'https://www.virustotal.com/api/v3'
            },
            'abuseipdb': {
                'enabled': self.config.get('abuseipdb', {}).get('enabled', False),
                'api_key': self.config.get('abuseipdb', {}).get('api_key', ''),
                'base_url': 'https://api.abuseipdb.com/api/v2'
            },
            'shodan': {
                'enabled': self.config.get('shodan', {}).get('enabled', False),
                'api_key': self.config.get('shodan', {}).get('api_key', ''),
                'base_url': 'https://api.shodan.io'
            },
            'censys': {
                'enabled': self.config.get('censys', {}).get('enabled', False),
                'api_id': self.config.get('censys', {}).get('api_id', ''),
                'api_secret': self.config.get('censys', {}).get('api_secret', ''),
                'base_url': 'https://search.censys.io/api/v2'
            }
        }

    def _init_ai_analyzer(self):
        """Initialize AI analyzer for threat correlation"""
        try:
            from .ai_analyzer import AIAnalyzer
            return AIAnalyzer()
        except ImportError:
            logger.warning("AI analyzer not available")
            return None

    def analyze_domain(self, domain: str, deep_scan: bool = False) -> Dict[str, Any]:
        """
        Analyze a domain for threat intelligence

        Args:
            domain: Domain to analyze
            deep_scan: Enable deep scanning with multiple feeds

        Returns:
            Threat intelligence analysis
        """
        logger.info(f"Analyzing domain: {domain}")

        analysis = {
            'domain': domain,
            'analyzed_at': datetime.now().isoformat(),
            'threat_level': 'unknown',
            'risk_score': 0.0,
            'indicators': [],
            'related_threats': [],
            'technologies': [],
            'reputation': {},
            'malware_families': [],
            'recommendations': []
        }

        # Check VirusTotal
        if self.threat_feeds['virustotal']['enabled']:
            vt_results = self._check_virustotal_domain(domain)
            analysis.update(vt_results)

        # Check Shodan for technologies
        if self.threat_feeds['shodan']['enabled']:
            shodan_results = self._check_shodan_domain(domain)
            analysis['technologies'] = shodan_results.get('technologies', [])

        # AI correlation
        if self.ai_analyzer:
            ai_analysis = self._ai_correlate_threats(analysis)
            analysis['ai_insights'] = ai_analysis

        # Calculate risk score
        analysis['risk_score'] = self._calculate_risk_score(analysis)
        analysis['threat_level'] = self._determine_threat_level(analysis['risk_score'])

        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def analyze_ip(self, ip: str, deep_scan: bool = False) -> Dict[str, Any]:
        """
        Analyze an IP address for threat intelligence

        Args:
            ip: IP address to analyze
            deep_scan: Enable deep scanning with multiple feeds

        Returns:
            Threat intelligence analysis
        """
        logger.info(f"Analyzing IP: {ip}")

        # Validate IP
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return {'error': 'Invalid IP address', 'ip': ip}

        analysis = {
            'ip': ip,
            'analyzed_at': datetime.now().isoformat(),
            'threat_level': 'unknown',
            'risk_score': 0.0,
            'abuse_confidence': 0,
            'reports': [],
            'geolocation': {},
            'asn': {},
            'ports': [],
            'vulnerabilities': [],
            'malware': [],
            'recommendations': []
        }

        # Check AbuseIPDB
        if self.threat_feeds['abuseipdb']['enabled']:
            abuse_results = self._check_abuseipdb(ip)
            analysis.update(abuse_results)

        # Check VirusTotal
        if self.threat_feeds['virustotal']['enabled']:
            vt_results = self._check_virustotal_ip(ip)
            analysis.update(vt_results)

        # Check Shodan
        if self.threat_feeds['shodan']['enabled']:
            shodan_results = self._check_shodan_ip(ip)
            analysis.update(shodan_results)

        # AI correlation
        if self.ai_analyzer:
            ai_analysis = self._ai_correlate_threats(analysis)
            analysis['ai_insights'] = ai_analysis

        # Calculate risk score
        analysis['risk_score'] = self._calculate_risk_score(analysis)
        analysis['threat_level'] = self._determine_threat_level(analysis['risk_score'])

        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def analyze_technology(self, technology: str, version: str = None) -> Dict[str, Any]:
        """
        Analyze a technology for known vulnerabilities and threats

        Args:
            technology: Technology name (e.g., nginx, apache)
            version: Version (optional)

        Returns:
            Technology threat analysis
        """
        logger.info(f"Analyzing technology: {technology} {version or ''}")

        analysis = {
            'technology': technology,
            'version': version,
            'analyzed_at': datetime.now().isoformat(),
            'cves': [],
            'exploits_available': False,
            'risk_score': 0.0,
            'patch_status': 'unknown',
            'recommendations': []
        }

        # Check for CVEs (placeholder - would use NVD API in production)
        cves = self._check_cves(technology, version)
        analysis['cves'] = cves

        # Check for exploits (placeholder - would use ExploitDB)
        exploits = self._check_exploits(technology, version)
        analysis['exploits_available'] = len(exploits) > 0
        analysis['exploits'] = exploits

        # Calculate risk score
        if cves:
            max_cvss = max(cve.get('cvss', 0) for cve in cves)
            analysis['risk_score'] = max_cvss

        # AI analysis
        if self.ai_analyzer:
            ai_analysis = self._ai_analyze_technology(technology, version, cves)
            analysis['ai_insights'] = ai_analysis

        # Generate recommendations
        analysis['recommendations'] = self._generate_tech_recommendations(analysis)

        return analysis

    def _check_virustotal_domain(self, domain: str) -> Dict[str, Any]:
        """Check domain against VirusTotal"""
        if not self.threat_feeds['virustotal']['enabled']:
            return {}

        try:
            headers = {'x-apikey': self.threat_feeds['virustotal']['api_key']}
            url = f"{self.threat_feeds['virustotal']['base_url']}/domains/{domain}"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})

                return {
                    'reputation': {
                        'malicious': stats.get('malicious', 0),
                        'suspicious': stats.get('suspicious', 0),
                        'harmless': stats.get('harmless', 0),
                        'total': sum(stats.values())
                    },
                    'last_analysis': data.get('data', {}).get('attributes', {}).get('last_analysis_date')
                }
            else:
                logger.warning(f"VirusTotal API error: {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"VirusTotal check failed: {e}")
            return {}

    def _check_virustotal_ip(self, ip: str) -> Dict[str, Any]:
        """Check IP against VirusTotal"""
        if not self.threat_feeds['virustotal']['enabled']:
            return {}

        try:
            headers = {'x-apikey': self.threat_feeds['virustotal']['api_key']}
            url = f"{self.threat_feeds['virustotal']['base_url']}/ip_addresses/{ip}"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})

                return {
                    'reputation': {
                        'malicious': stats.get('malicious', 0),
                        'suspicious': stats.get('suspicious', 0),
                        'harmless': stats.get('harmless', 0),
                        'total': sum(stats.values())
                    }
                }
            else:
                return {}

        except Exception as e:
            logger.error(f"VirusTotal IP check failed: {e}")
            return {}

    def _check_abuseipdb(self, ip: str) -> Dict[str, Any]:
        """Check IP against AbuseIPDB"""
        if not self.threat_feeds['abuseipdb']['enabled']:
            return {}

        try:
            headers = {'Key': self.threat_feeds['abuseipdb']['api_key']}
            params = {'ipAddress': ip, 'maxAgeInDays': 90}
            url = f"{self.threat_feeds['abuseipdb']['base_url']}/check"

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json().get('data', {})

                return {
                    'abuse_confidence': data.get('abuseConfidenceScore', 0),
                    'reports': data.get('totalReports', 0),
                    'last_reported': data.get('lastReportedAt'),
                    'country_code': data.get('countryCode'),
                    'usage_type': data.get('usageType')
                }
            else:
                return {}

        except Exception as e:
            logger.error(f"AbuseIPDB check failed: {e}")
            return {}

    def _check_shodan_domain(self, domain: str) -> Dict[str, Any]:
        """Check domain against Shodan"""
        if not self.threat_feeds['shodan']['enabled']:
            return {}

        try:
            # Shodan doesn't have direct domain search, use DNS search
            params = {'key': self.threat_feeds['shodan']['api_key'], 'query': f'hostname:{domain}'}
            url = f"{self.threat_feeds['shodan']['base_url']}/shodan/host/search"

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get('matches', [])

                technologies = set()
                for result in results[:10]:  # Limit to top 10
                    technologies.update(result.get('tags', []))

                return {
                    'technologies': list(technologies),
                    'host_count': data.get('total', 0)
                }
            else:
                return {}

        except Exception as e:
            logger.error(f"Shodan domain check failed: {e}")
            return {}

    def _check_shodan_ip(self, ip: str) -> Dict[str, Any]:
        """Check IP against Shodan"""
        if not self.threat_feeds['shodan']['enabled']:
            return {}

        try:
            params = {'key': self.threat_feeds['shodan']['api_key']}
            url = f"{self.threat_feeds['shodan']['base_url']}/shodan/host/{ip}"

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                return {
                    'ports': data.get('ports', []),
                    'vulnerabilities': data.get('vulns', []),
                    'os': data.get('os', {}),
                    'asn': data.get('asn', ''),
                    'country_name': data.get('country_name', '')
                }
            else:
                return {}

        except Exception as e:
            logger.error(f"Shodan IP check failed: {e}")
            return {}

    def _check_cves(self, technology: str, version: str = None) -> List[Dict[str, Any]]:
        """Check for CVEs (placeholder)"""
        # In production, would query NVD API
        # For now, return placeholder data
        return [
            {
                'cve_id': 'CVE-2021-XXXX',
                'description': f'Vulnerability in {technology}',
                'cvss': 7.5,
                'published': '2021-01-01'
            }
        ]

    def _check_exploits(self, technology: str, version: str = None) -> List[Dict[str, Any]]:
        """Check for exploits (placeholder)"""
        # In production, would query ExploitDB
        return []

    def _ai_correlate_threats(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to correlate threat intelligence"""
        if not self.ai_analyzer:
            return {}

        try:
            # Build context for AI
            context = json.dumps(analysis, indent=2)

            result = self.ai_analyzer.analyze(
                tool_name='threat_intel',
                task='correlate_threats',
                content=context
            )

            return result.get('analysis', {})

        except Exception as e:
            logger.error(f"AI correlation failed: {e}")
            return {}

    def _ai_analyze_technology(self, technology: str, version: str,
                                cves: List[Dict]) -> Dict[str, Any]:
        """Use AI to analyze technology threats"""
        if not self.ai_analyzer:
            return {}

        try:
            context = f"Technology: {technology}\nVersion: {version}\nCVEs: {len(cves)}"

            result = self.ai_analyzer.analyze(
                tool_name='threat_intel',
                task='analyze_technology',
                content=context
            )

            return result.get('analysis', {})

        except Exception as e:
            logger.error(f"AI technology analysis failed: {e}")
            return {}

    def _calculate_risk_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall risk score"""
        score = 0.0

        # Reputation score
        reputation = analysis.get('reputation', {})
        if reputation:
            total = reputation.get('total', 1)
            malicious = reputation.get('malicious', 0)
            suspicious = reputation.get('suspicious', 0)
            score += ((malicious + suspicious) / total) * 10

        # Abuse confidence
        abuse_confidence = analysis.get('abuse_confidence', 0)
        score += abuse_confidence / 10

        # Vulnerabilities
        cves = analysis.get('cves', [])
        if cves:
            max_cvss = max(cve.get('cvss', 0) for cve in cves)
            score += max_cvss

        # Exploits available
        if analysis.get('exploits_available', False):
            score += 2.0

        return min(score, 10.0)

    def _determine_threat_level(self, risk_score: float) -> str:
        """Determine threat level from risk score"""
        if risk_score >= 8.0:
            return 'critical'
        elif risk_score >= 6.0:
            return 'high'
        elif risk_score >= 4.0:
            return 'medium'
        elif risk_score >= 2.0:
            return 'low'
        else:
            return 'info'

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []

        risk_score = analysis.get('risk_score', 0)

        if risk_score >= 8.0:
            recommendations.append("CRITICAL: Immediate action required - high threat detected")
            recommendations.append("Block this IP/domain immediately")
            recommendations.append("Investigate all associated systems")

        elif risk_score >= 6.0:
            recommendations.append("HIGH: Block or heavily monitor this target")
            recommendations.append("Review logs for suspicious activity")

        elif risk_score >= 4.0:
            recommendations.append("MEDIUM: Monitor this target closely")
            recommendations.append("Consider adding to watchlist")

        if analysis.get('vulnerabilities'):
            recommendations.append("Apply security patches for identified vulnerabilities")

        if analysis.get('exploits_available'):
            recommendations.append("Exploits are available - patch immediately")

        return recommendations

    def _generate_tech_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate technology-specific recommendations"""
        recommendations = []

        if analysis.get('cves'):
            recommendations.append(f"Apply security patches for {len(analysis['cves'])} CVEs")

        if analysis.get('exploits_available'):
            recommendations.append("Exploits are publicly available - patch immediately")

        if analysis.get('risk_score', 0) >= 7.0:
            recommendations.append("Consider upgrading to latest version")

        recommendations.append("Monitor for security advisories")
        recommendations.append("Implement defense-in-depth measures")

        return recommendations


def main():
    """Main entry point for testing"""
    analyzer = ThreatIntelligenceAnalyzer()

    # Test domain analysis
    result = analyzer.analyze_domain('example.com')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
