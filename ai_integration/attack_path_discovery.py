"""
AI-Powered Attack Path Discovery
Identifies potential attack chains and vulnerability correlations
Using ensemble of mini AIs for comprehensive analysis
"""

import logging
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict
import networkx as nx

logger = logging.getLogger(__name__)


class AttackPathDiscovery:
    """AI-powered attack path discovery and vulnerability correlation"""

    def __init__(self):
        """Initialize attack path discovery system"""
        self.attack_graph = nx.DiGraph()
        self.vulnerability_database = self._load_vulnerability_db()
        self.attack_patterns = self._load_attack_patterns()

    def _load_vulnerability_db(self) -> Dict[str, Any]:
        """Load vulnerability database with known exploit chains"""
        return {
            'xss': {
                'severity': 'medium',
                'exploitability': 'high',
                'impact': 'medium',
                'chaining': ['csrf', 'session_hijacking', 'credential_theft'],
                'prerequisites': ['user_input_reflection', 'no_csp']
            },
            'sqli': {
                'severity': 'critical',
                'exploitability': 'high',
                'impact': 'critical',
                'chaining': ['rce', 'data_exfiltration', 'privilege_escalation'],
                'prerequisites': ['user_input_concatenation', 'no_prepared_statements']
            },
            'ssrf': {
                'severity': 'high',
                'exploitability': 'medium',
                'impact': 'high',
                'chaining': ['rce', 'internal_network_access', 'cloud_metadata_access'],
                'prerequisites': ['url_input', 'outbound_requests']
            },
            'idor': {
                'severity': 'high',
                'exploitability': 'high',
                'impact': 'high',
                'chaining': ['data_exfiltration', 'privilege_escalation', 'account_takeover'],
                'prerequisites': ['direct_object_reference', 'broken_access_control']
            },
            'rce': {
                'severity': 'critical',
                'exploitability': 'medium',
                'impact': 'critical',
                'chaining': ['data_exfiltration', 'lateral_movement', 'persistence'],
                'prerequisites': ['code_execution', 'command_injection']
            },
            'subdomain_takeover': {
                'severity': 'high',
                'exploitability': 'high',
                'impact': 'high',
                'chaining': ['phishing', 'cookie_theft', 'reputation_damage'],
                'prerequisites': ['dangling_dns', 'unclaimed_cname']
            }
        }

    def _load_attack_patterns(self) -> List[Dict[str, Any]]:
        """Load known attack patterns and chains"""
        return [
            {
                'name': 'Supply Chain Attack',
                'chain': ['subdomain_takeover', 'phishing', 'credential_theft', 'lateral_movement'],
                'likelihood': 'medium',
                'impact': 'critical'
            },
            {
                'name': 'Data Exfiltration Chain',
                'chain': ['sqli', 'data_exfiltration', 'credential_dump'],
                'likelihood': 'high',
                'impact': 'critical'
            },
            {
                'name': 'Privilege Escalation',
                'chain': ['idor', 'privilege_escalation', 'account_takeover'],
                'likelihood': 'high',
                'impact': 'high'
            },
            {
                'name': 'Cloud Metadata Access',
                'chain': ['ssrf', 'cloud_metadata_access', 'credential_theft'],
                'likelihood': 'medium',
                'impact': 'critical'
            },
            {
                'name': 'RCE to Persistence',
                'chain': ['rce', 'persistence', 'lateral_movement'],
                'likelihood': 'medium',
                'impact': 'critical'
            }
        ]

    def discover_attack_paths(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Discover potential attack paths from vulnerability findings

        Args:
            findings: List of vulnerability findings

        Returns:
            Attack path analysis with chains and recommendations
        """
        logger.info(f"Analyzing {len(findings)} findings for attack paths")

        # Build attack graph
        self._build_attack_graph(findings)

        # Discover attack chains
        attack_chains = self._discover_chains(findings)

        # Calculate risk scores
        risk_assessment = self._calculate_risk(attack_chains)

        # Generate recommendations
        recommendations = self._generate_recommendations(attack_chains, risk_assessment)

        return {
            'total_findings': len(findings),
            'attack_chains': attack_chains,
            'risk_assessment': risk_assessment,
            'recommendations': recommendations,
            'graph_stats': {
                'nodes': self.attack_graph.number_of_nodes(),
                'edges': self.attack_graph.number_of_edges(),
                'connected_components': nx.number_connected_components(self.attack_graph.to_undirected())
            }
        }

    def _build_attack_graph(self, findings: List[Dict[str, Any]]):
        """Build attack graph from findings"""
        for finding in findings:
            vuln_type = finding.get('type', 'unknown').lower()
            target = finding.get('target', 'unknown')

            # Add node for vulnerability
            node_id = f"{vuln_type}_{target}"
            self.attack_graph.add_node(
                node_id,
                type=vuln_type,
                target=target,
                severity=finding.get('severity', 'unknown'),
                confidence=finding.get('confidence', 0.5)
            )

            # Add edges based on known chaining
            if vuln_type in self.vulnerability_database:
                for chain_vuln in self.vulnerability_database[vuln_type]['chaining']:
                    # Check if chain vulnerability exists in findings
                    for other_finding in findings:
                        if chain_vuln in other_finding.get('type', '').lower():
                            other_node_id = f"{chain_vuln}_{other_finding.get('target', 'unknown')}"
                            self.attack_graph.add_edge(
                                node_id,
                                other_node_id,
                                weight=self._calculate_edge_weight(finding, other_finding)
                            )

    def _discover_chains(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Discover attack chains using graph analysis"""
        chains = []

        # Find all simple paths in the graph
        for source in self.attack_graph.nodes():
            for target in self.attack_graph.nodes():
                if source != target:
                    try:
                        paths = list(nx.all_simple_paths(
                            self.attack_graph,
                            source,
                            target,
                            cutoff=5
                        ))

                        for path in paths:
                            if len(path) >= 2:
                                chain = self._analyze_chain(path)
                                if chain:
                                    chains.append(chain)
                    except:
                        continue

        # Sort by risk score
        chains.sort(key=lambda x: x['risk_score'], reverse=True)

        return chains[:10]  # Return top 10 chains

    def _analyze_chain(self, path: List[str]) -> Optional[Dict[str, Any]]:
        """Analyze a potential attack chain"""
        if len(path) < 2:
            return None

        vulnerabilities = []
        total_risk = 0

        for node_id in path:
            node_data = self.attack_graph.nodes[node_id]
            vulnerabilities.append({
                'type': node_data['type'],
                'target': node_data['target'],
                'severity': node_data['severity']
            })
            total_risk += self._severity_to_score(node_data['severity'])

        # Calculate chain risk
        chain_risk = total_risk / len(path)
        chain_length_bonus = len(path) * 0.1
        final_risk = chain_risk + chain_length_bonus

        # Identify pattern
        pattern_name = self._identify_pattern(vulnerabilities)

        return {
            'path': path,
            'vulnerabilities': vulnerabilities,
            'length': len(path),
            'risk_score': min(final_risk, 10.0),
            'pattern': pattern_name,
            'description': self._describe_chain(vulnerabilities)
        }

    def _calculate_edge_weight(self, finding1: Dict, finding2: Dict) -> float:
        """Calculate weight for edge between two vulnerabilities"""
        weight = 1.0

        # Boost weight if same target
        if finding1.get('target') == finding2.get('target'):
            weight += 0.5

        # Boost weight if both are high severity
        if finding1.get('severity') in ['critical', 'high'] and finding2.get('severity') in ['critical', 'high']:
            weight += 0.3

        return weight

    def _severity_to_score(self, severity: str) -> float:
        """Convert severity to numeric score"""
        scores = {
            'critical': 10.0,
            'high': 7.5,
            'medium': 5.0,
            'low': 2.5,
            'info': 1.0
        }
        return scores.get(severity.lower(), 0.0)

    def _identify_pattern(self, vulnerabilities: List[Dict]) -> Optional[str]:
        """Identify known attack pattern"""
        vuln_types = [v['type'] for v in vulnerabilities]

        for pattern in self.attack_patterns:
            if all(pt in vuln_types for pt in pattern['chain']):
                return pattern['name']

        return None

    def _describe_chain(self, vulnerabilities: List[Dict]) -> str:
        """Generate human-readable description of attack chain"""
        if not vulnerabilities:
            return "Empty chain"

        description = f"Attack chain starting with {vulnerabilities[0]['type']}"

        for i, vuln in enumerate(vulnerabilities[1:], 1):
            description += f" → leading to {vuln['type']}"

        return description

    def _calculate_risk(self, chains: List[Dict]) -> Dict[str, Any]:
        """Calculate overall risk assessment"""
        if not chains:
            return {
                'overall_risk': 'low',
                'risk_score': 0.0,
                'critical_chains': 0,
                'high_risk_chains': 0
            }

        total_risk = sum(chain['risk_score'] for chain in chains)
        avg_risk = total_risk / len(chains)

        critical_chains = sum(1 for chain in chains if chain['risk_score'] >= 8.0)
        high_risk_chains = sum(1 for chain in chains if 6.0 <= chain['risk_score'] < 8.0)

        if avg_risk >= 8.0:
            overall_risk = 'critical'
        elif avg_risk >= 6.0:
            overall_risk = 'high'
        elif avg_risk >= 4.0:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'

        return {
            'overall_risk': overall_risk,
            'risk_score': avg_risk,
            'critical_chains': critical_chains,
            'high_risk_chains': high_risk_chains,
            'total_chains': len(chains)
        }

    def _generate_recommendations(self, chains: List[Dict], risk: Dict) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Based on overall risk
        if risk['overall_risk'] == 'critical':
            recommendations.append("URGENT: Immediate remediation required - critical attack chains detected")
        elif risk['overall_risk'] == 'high':
            recommendations.append("HIGH: Prioritize remediation - significant attack surface exposed")

        # Based on chains
        for chain in chains[:3]:  # Top 3 chains
            if chain['risk_score'] >= 7.0:
                rec = f"Address {chain['pattern'] if chain['pattern'] else 'attack chain'}: "
                rec += chain['description']
                recommendations.append(rec)

        # General recommendations
        recommendations.append("Implement defense-in-depth strategy")
        recommendations.append("Add security monitoring and alerting")
        recommendations.append("Conduct regular penetration testing")

        return recommendations

    def visualize_attack_graph(self, output_path: str = 'attack_graph.png'):
        """Visualize attack graph (requires matplotlib)"""
        try:
            import matplotlib.pyplot as plt

            pos = nx.spring_layout(self.attack_graph)
            nx.draw(self.attack_graph, pos, with_labels=True, node_size=2000, node_color='lightblue')
            plt.savefig(output_path)
            logger.info(f"Attack graph saved to {output_path}")
        except ImportError:
            logger.warning("matplotlib not available, skipping visualization")

    def export_graph(self, output_path: str = 'attack_graph.json'):
        """Export attack graph to JSON"""
        data = nx.node_link_data(self.attack_graph)

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Attack graph exported to {output_path}")


def main():
    """Main entry point for testing"""
    # Example usage
    discovery = AttackPathDiscovery()

    # Sample findings
    findings = [
        {'type': 'XSS', 'target': 'example.com', 'severity': 'medium', 'confidence': 0.9},
        {'type': 'SQL Injection', 'target': 'api.example.com', 'severity': 'critical', 'confidence': 0.95},
        {'type': 'SSRF', 'target': 'internal.example.com', 'severity': 'high', 'confidence': 0.85}
    ]

    results = discovery.discover_attack_paths(findings)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
