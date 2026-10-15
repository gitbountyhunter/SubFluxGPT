"""
Ninja Automator - Aggressive AI-Powered Security Automation
Multi-vector attack automation with AI decision-making
For authorized security testing only
"""

import logging
import json
import asyncio
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

logger = logging.getLogger(__name__)


class NinjaAutomator:
    """Aggressive AI-powered security automation for ninjas"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize ninja automator

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.attack_chains = self._load_attack_chains()
        self.ai_analyzer = self._init_ai()
        self.target_queue = []
        self.results = []

    def _load_attack_chains(self) -> List[Dict[str, Any]]:
        """Load pre-configured attack chains"""
        return [
            {
                'name': 'Subdomain Takeover Chain',
                'tools': ['subfinder', 'assetfinder', 'amass'],
                'follow_up': ['httpx', 'nuclei -t takeover'],
                'ai_decisions': ['prioritize_dangling', 'check_cname_records']
            },
            {
                'name': 'Injection Hunt Chain',
                'tools': ['katana', 'waybackurls', 'gau'],
                'follow_up': ['ffuf', 'sqlmap', 'xsser'],
                'ai_decisions': ['identify_params', 'test_injection_points']
            },
            {
                'name': 'Cloud Infrastructure Chain',
                'tools': ['subfinder', 'dnsx', 'subjs'],
                'follow_up': ['nuclei -t cloud', 'ssrf_map'],
                'ai_decisions': ['detect_cloud_services', 'map_attack_surface']
            },
            {
                'name': 'API Discovery Chain',
                'tools': ['subfinder', 'httpx', 'katana'],
                'follow_up': ['arjun', 'ffuf -mode bruteforce', 'nuclei -t api'],
                'ai_decisions': ['discover_endpoints', 'test_auth_bypass']
            },
            {
                'name': 'Parameter Tamper Chain',
                'tools': ['waybackurls', 'gau'],
                'follow_up': ['paramspider', 'arjun', 'nuclei -t idor'],
                'ai_decisions': ['extract_params', 'test_idor']
            }
        ]

    def _init_ai(self):
        """Initialize AI analyzer"""
        try:
            from .ai_analyzer import AIAnalyzer
            return AIAnalyzer()
        except ImportError:
            logger.warning("AI analyzer not available")
            return None

    def auto_pwn(self, target: str, chain_name: str = 'auto',
                 intensity: str = 'aggressive') -> Dict[str, Any]:
        """
        Automated security testing with AI decision-making

        Args:
            target: Target domain
            chain_name: Attack chain to use (or 'auto' for AI selection)
            intensity: Testing intensity (stealth, normal, aggressive)

        Returns:
            Attack results with findings
        """
        logger.info(f"🥷 Starting auto-pwn on {target} with {intensity} intensity")

        results = {
            'target': target,
            'started_at': datetime.now().isoformat(),
            'chain': chain_name,
            'intensity': intensity,
            'findings': [],
            'ai_decisions': [],
            'vulnerabilities': [],
            'risk_score': 0.0
        }

        # Select attack chain
        if chain_name == 'auto':
            chain = self._ai_select_chain(target)
            results['chain'] = chain['name']
        else:
            chain = next((c for c in self.attack_chains if c['name'] == chain_name), self.attack_chains[0])

        logger.info(f"🎯 Selected chain: {chain['name']}")

        # Execute reconnaissance phase
        recon_results = self._execute_recon(target, chain['tools'], intensity)
        results['recon'] = recon_results

        # AI analysis of recon results
        if self.ai_analyzer:
            ai_decisions = self._ai_analyze_recon(recon_results, chain['ai_decisions'])
            results['ai_decisions'] = ai_decisions

        # Execute follow-up attacks based on AI decisions
        attack_results = self._execute_attacks(target, chain['follow_up'], ai_decisions if self.ai_analyzer else [], intensity)
        results['attack_results'] = attack_results

        # Correlate findings
        results['vulnerabilities'] = self._correlate_findings(recon_results, attack_results)

        # Calculate risk score
        results['risk_score'] = self._calculate_risk(results['vulnerabilities'])

        results['completed_at'] = datetime.now().isoformat()

        logger.info(f"✅ Auto-pwn complete on {target}. Risk score: {results['risk_score']:.1f}")

        return results

    def _ai_select_chain(self, target: str) -> Dict[str, Any]:
        """Use AI to select optimal attack chain"""
        if not self.ai_analyzer:
            return self.attack_chains[0]

        try:
            # Simple heuristic for now - in production, would use actual AI
            return random.choice(self.attack_chains)
        except Exception as e:
            logger.error(f"AI chain selection failed: {e}")
            return self.attack_chains[0]

    def _execute_recon(self, target: str, tools: List[str],
                       intensity: str) -> Dict[str, Any]:
        """Execute reconnaissance tools"""
        logger.info(f"🔍 Running reconnaissance with {len(tools)} tools")

        results = {}

        # Execute tools in parallel for speed
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for tool in tools:
                future = executor.submit(self._run_tool, tool, target, intensity)
                futures[future] = tool

            for future in as_completed(futures):
                tool = futures[future]
                try:
                    result = future.result()
                    results[tool] = result
                    logger.info(f"✓ {tool} completed")
                except Exception as e:
                    logger.error(f"✗ {tool} failed: {e}")
                    results[tool] = {'error': str(e)}

        return results

    def _execute_attacks(self, target: str, attack_commands: List[str],
                         ai_decisions: List[str], intensity: str) -> Dict[str, Any]:
        """Execute attack commands based on AI decisions"""
        logger.info(f"⚔️ Executing {len(attack_commands)} attack commands")

        results = {}

        for cmd in attack_commands:
            # Modify command based on AI decisions
            modified_cmd = self._modify_command(cmd, ai_decisions, intensity)

            try:
                result = self._run_tool(modified_cmd.split()[0], target, intensity, extra_args=modified_cmd.split()[1:])
                results[cmd] = result
                logger.info(f"✓ Attack command completed: {cmd}")
            except Exception as e:
                logger.error(f"✗ Attack command failed: {cmd} - {e}")
                results[cmd] = {'error': str(e)}

        return results

    def _run_tool(self, tool: str, target: str, intensity: str,
                  extra_args: List[str] = None) -> Dict[str, Any]:
        """Run a security tool"""
        extra_args = extra_args or []

        # Build command based on tool
        cmd_map = {
            'subfinder': ['subfinder', '-d', target, '-silent'],
            'assetfinder': ['assetfinder', '--subs-only', target],
            'amass': ['amass', 'enum', '-passive', '-d', target],
            'httpx': ['httpx', '-u', target, '-silent', '-json'],
            'katana': ['katana', '-u', f'https://{target}', '-silent', '-json'],
            'waybackurls': ['waybackurls', target],
            'gau': ['gau', target],
            'nuclei': ['nuclei', '-u', target, '-silent', '-json'],
            'ffuf': ['ffuf', '-u', f'https://{target}/FUZZ', '-w', '/usr/share/wordlists/dirb/common.txt'],
            'sqlmap': ['sqlmap', '-u', f'https://{target}', '--batch', '--random-agent'],
            'arjun': ['arjun', '-u', f'https://{target}'],
            'dnsx': ['dnsx', '-d', target, '-silent'],
            'subjs': ['subjs', '-u', target]
        }

        base_cmd = cmd_map.get(tool, [tool])

        # Add intensity modifiers
        if intensity == 'aggressive':
            base_cmd.extend(['-timeout', '30', '-rate-limit', '100'])
        elif intensity == 'stealth':
            base_cmd.extend(['-timeout', '10', '-rate-limit', '10', '-random-agent'])

        # Add extra args
        base_cmd.extend(extra_args)

        try:
            result = subprocess.run(
                base_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            return {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {'error': 'Tool timed out', 'success': False}
        except Exception as e:
            return {'error': str(e), 'success': False}

    def _ai_analyze_recon(self, recon_results: Dict[str, Any],
                          ai_tasks: List[str]) -> List[str]:
        """Use AI to analyze reconnaissance results"""
        if not self.ai_analyzer:
            return []

        decisions = []

        for task in ai_tasks:
            try:
                context = json.dumps(recon_results, indent=2)
                result = self.ai_analyzer.analyze(
                    tool_name='ninja_automator',
                    task=task,
                    content=context
                )
                decisions.append(result.get('analysis', task))
            except Exception as e:
                logger.error(f"AI analysis failed for {task}: {e}")

        return decisions

    def _modify_command(self, command: str, ai_decisions: List[str],
                       intensity: str) -> str:
        """Modify command based on AI decisions"""
        modified = command

        # Add AI-suggested modifications
        for decision in ai_decisions:
            if 'dangling' in decision.lower():
                modified += ' -t takeover'
            elif 'cloud' in decision.lower():
                modified += ' -t cloud-metadata'
            elif 'params' in decision.lower():
                modified += ' -depth 3'

        # Add intensity modifiers
        if intensity == 'aggressive':
            modified += ' -stats'
        elif intensity == 'stealth':
            modified += ' -delay 1000ms'

        return modified

    def _correlate_findings(self, recon_results: Dict[str, Any],
                            attack_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Correlate findings from recon and attack phases"""
        vulnerabilities = []

        # Extract findings from attack results
        for cmd, result in attack_results.items():
            if result.get('success') and result.get('stdout'):
                # Parse nuclei output
                if 'nuclei' in cmd.lower():
                    lines = result['stdout'].split('\n')
                    for line in lines:
                        if line.strip():
                            vulnerabilities.append({
                                'tool': 'nuclei',
                                'finding': line.strip(),
                                'severity': self._extract_severity(line)
                            })

        # Correlate with recon data
        for tool, result in recon_results.items():
            if result.get('success') and result.get('stdout'):
                # Look for suspicious patterns
                if 'subfinder' in tool.lower() or 'assetfinder' in tool.lower():
                    subdomains = result['stdout'].split('\n')
                    for subdomain in subdomains:
                        if self._is_suspicious_subdomain(subdomain):
                            vulnerabilities.append({
                                'tool': tool,
                                'finding': f"Suspicious subdomain: {subdomain}",
                                'severity': 'medium',
                                'type': 'suspicious_subdomain'
                            })

        return vulnerabilities

    def _extract_severity(self, line: str) -> str:
        """Extract severity from nuclei output"""
        line_lower = line.lower()
        if 'critical' in line_lower:
            return 'critical'
        elif 'high' in line_lower:
            return 'high'
        elif 'medium' in line_lower:
            return 'medium'
        elif 'low' in line_lower:
            return 'low'
        else:
            return 'info'

    def _is_suspicious_subdomain(self, subdomain: str) -> bool:
        """Check if subdomain looks suspicious"""
        suspicious_keywords = ['dev', 'test', 'staging', 'old', 'deprecated', 'backup']
        subdomain_lower = subdomain.lower()

        return any(kw in subdomain_lower for kw in suspicious_keywords)

    def _calculate_risk(self, vulnerabilities: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score"""
        if not vulnerabilities:
            return 0.0

        total_score = 0
        severity_scores = {
            'critical': 10.0,
            'high': 7.5,
            'medium': 5.0,
            'low': 2.5,
            'info': 1.0
        }

        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'info')
            total_score += severity_scores.get(severity, 1.0)

        return min(total_score / len(vulnerabilities), 10.0)

    def swarm_attack(self, targets: List[str], chain_name: str = 'auto',
                     intensity: str = 'normal', max_concurrent: int = 5) -> Dict[str, Any]:
        """
        Swarm attack multiple targets simultaneously

        Args:
            targets: List of target domains
            chain_name: Attack chain to use
            intensity: Testing intensity
            max_concurrent: Maximum concurrent attacks

        Returns:
            Combined results from all targets
        """
        logger.info(f"🐝 Swarm attack on {len(targets)} targets")

        results = {
            'started_at': datetime.now().isoformat(),
            'targets': targets,
            'chain': chain_name,
            'intensity': intensity,
            'target_results': {},
            'total_vulnerabilities': 0,
            'avg_risk_score': 0.0
        }

        # Execute attacks in parallel
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = {}
            for target in targets:
                future = executor.submit(self.auto_pwn, target, chain_name, intensity)
                futures[future] = target

            for future in as_completed(futures):
                target = futures[future]
                try:
                    result = future.result()
                    results['target_results'][target] = result
                    logger.info(f"✓ Completed attack on {target}")
                except Exception as e:
                    logger.error(f"✗ Attack failed on {target}: {e}")
                    results['target_results'][target] = {'error': str(e)}

        # Calculate aggregate statistics
        total_vulns = 0
        total_risk = 0
        successful_targets = 0

        for target, result in results['target_results'].items():
            if 'vulnerabilities' in result:
                total_vulns += len(result['vulnerabilities'])
                total_risk += result.get('risk_score', 0)
                successful_targets += 1

        results['total_vulnerabilities'] = total_vulns
        results['avg_risk_score'] = total_risk / successful_targets if successful_targets > 0 else 0
        results['completed_at'] = datetime.now().isoformat()

        logger.info(f"✅ Swarm complete. Total vulns: {total_vulns}, Avg risk: {results['avg_risk_score']:.1f}")

        return results

    def generate_one_liner(self, target: str, chain_name: str = 'auto') -> str:
        """Generate ninja-style one-liner command"""
        if chain_name == 'auto':
            chain = self.attack_chains[0]
        else:
            chain = next((c for c in self.attack_chains if c['name'] == chain_name), self.attack_chains[0])

        tools_str = ' | '.join(chain['tools'])
        return f"subfinder -d {target} -silent | {tools_str} | httpx -silent | nuclei -u {target} -silent"

    def export_results(self, results: Dict[str, Any], output_path: str):
        """Export results to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results exported to {output_path}")


def main():
    """Main entry point for testing"""
    automator = NinjaAutomator()

    # Test single target
    result = automator.auto_pwn('example.com', chain_name='auto', intensity='normal')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
