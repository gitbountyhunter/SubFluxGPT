"""
AI Analyzer - Mini AI Integration for Tool Output Analysis
Uses mini LLMs to analyze security tool outputs and provide insights
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI analyzer using mini LLMs for security tool output analysis"""

    def __init__(self, model_path: str = None, model_size: str = '124M'):
        """
        Initialize AI analyzer with mini LLM

        Args:
            model_path: Path to trained model
            model_size: Model size (124M, 350M, 774M, 1558M)
        """
        self.model_path = model_path
        self.model_size = model_size
        self.model = None
        self.tokenizer = None

        # Try to load the model
        self._load_model()

    def _load_model(self):
        """Load the mini LLM model"""
        try:
            # Try llama.cpp integration first (GGUF models)
            try:
                from llama_cpp import Llama
                if self.model_path:
                    self.model = Llama(
                        model_path=self.model_path,
                        n_ctx=2048,
                        n_threads=8,
                        verbose=False
                    )
                    logger.info(f"Loaded GGUF model from {self.model_path}")
                    return
            except ImportError:
                logger.debug("llama_cpp not available")

            # Try llm.c integration
            try:
                import sys
                sys.path.append('llm.c/llm.c-master')
                from train_gpt2 import GPT2
                # This would need proper model loading logic
                logger.info("llm.c integration available")
            except ImportError:
                logger.debug("llm.c integration not available")

            # Fallback: Use pattern-based analysis without model
            logger.warning("No model loaded, using pattern-based analysis")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    def analyze(self, tool_name: str, task: str, content: str) -> Dict[str, Any]:
        """
        Analyze tool output with AI

        Args:
            tool_name: Name of the security tool
            task: Analysis task (e.g., 'detect_vulnerabilities')
            content: Tool output to analyze

        Returns:
            Dict with analysis results
        """
        if self.model:
            return self._analyze_with_model(tool_name, task, content)
        else:
            return self._analyze_with_patterns(tool_name, task, content)

    def _analyze_with_model(self, tool_name: str, task: str, content: str) -> Dict[str, Any]:
        """Analyze using loaded mini LLM"""
        try:
            # Construct prompt for the model
            prompt = self._construct_prompt(tool_name, task, content)

            # Generate analysis
            response = self.model(
                prompt,
                max_tokens=512,
                temperature=0.3,
                stop=["\n\n", "###"]
            )

            analysis_text = response['choices'][0]['text'].strip()

            # Parse the response
            return self._parse_analysis(analysis_text, task)

        except Exception as e:
            logger.error(f"Model analysis failed: {e}")
            return self._analyze_with_patterns(tool_name, task, content)

    def _analyze_with_patterns(self, tool_name: str, task: str, content: str) -> Dict[str, Any]:
        """Analyze using pattern matching (fallback)"""
        analysis = {
            'method': 'pattern_based',
            'tool': tool_name,
            'task': task,
            'findings': [],
            'risk_level': 'info'
        }

        # Pattern-based analysis based on tool and task
        if tool_name == 'httpx' and task == 'detect_tech_stack':
            analysis['findings'] = self._detect_tech_patterns(content)
        elif tool_name == 'subfinder' and task == 'classify_subdomains':
            analysis['findings'] = self._classify_subdomain_patterns(content)
        elif tool_name == 'nuclei' and task == 'prioritize_findings':
            analysis['findings'] = self._prioritize_vulnerabilities(content)
        elif tool_name == 'dnsx' and task == 'detect_wildcards':
            analysis['findings'] = self._detect_wildcard_patterns(content)
        else:
            analysis['findings'] = [{'note': 'Pattern analysis not implemented for this task'}]

        return analysis

    def _construct_prompt(self, tool_name: str, task: str, content: str) -> str:
        """Construct analysis prompt for the model"""
        prompts = {
            'httpx': {
                'detect_tech_stack': f"Analyze these HTTP responses and identify the technology stack:\n\n{content}\n\nOutput in JSON format with technologies detected.",
                'find_vulnerabilities': f"Analyze these HTTP responses for potential security vulnerabilities:\n\n{content}\n\nList any security issues found."
            },
            'subfinder': {
                'classify_subdomains': f"Classify these subdomains by type (e.g., dev, staging, prod, api, cdn):\n\n{content}\n\nOutput classification.",
                'predict_takeover': f"Analyze these subdomains for potential subdomain takeover vulnerabilities:\n\n{content}\n\nFlag any suspicious ones."
            },
            'nuclei': {
                'prioritize_findings': f"Prioritize these vulnerability findings by severity:\n\n{content}\n\nRank from critical to low.",
                'analyze_chain': f"Analyze these vulnerability findings for potential attack chains:\n\n{content}\n\nIdentify connected vulnerabilities."
            }
        }

        if tool_name in prompts and task in prompts[tool_name]:
            return prompts[tool_name][task]
        else:
            return f"Analyze this {tool_name} output for {task}:\n\n{content}\n\nProvide analysis."

    def _parse_analysis(self, analysis_text: str, task: str) -> Dict[str, Any]:
        """Parse model analysis response"""
        try:
            # Try to parse as JSON
            parsed = json.loads(analysis_text)
            return {
                'method': 'model_based',
                'analysis': parsed,
                'raw_response': analysis_text
            }
        except json.JSONDecodeError:
            # Return as text
            return {
                'method': 'model_based',
                'analysis_text': analysis_text,
                'task': task
            }

    def _detect_tech_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect technology stack from HTTP responses"""
        tech_signatures = {
            'server': ['nginx', 'apache', 'cloudflare', 'awselb', 'iis'],
            'framework': ['express', 'django', 'flask', 'rails', 'laravel'],
            'cdn': ['cloudflare', 'fastly', 'akamai', 'cloudfront'],
            'language': ['php', 'python', 'ruby', 'java', 'node']
        }

        findings = []
        content_lower = content.lower()

        for category, signatures in tech_signatures.items():
            for sig in signatures:
                if sig in content_lower:
                    findings.append({
                        'category': category,
                        'technology': sig,
                        'confidence': 'medium'
                    })

        return findings

    def _classify_subdomain_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Classify subdomains by type"""
        patterns = {
            'dev': ['dev', 'development', 'test', 'staging'],
            'prod': ['www', 'app', 'api', 'prod', 'production'],
            'cdn': ['cdn', 'static', 'assets', 'media'],
            'regional': ['us-', 'eu-', 'asia-', 'na-']
        }

        findings = []
        lines = content.strip().split('\n')

        for line in lines:
            domain = line.strip()
            if not domain:
                continue

            for category, keywords in patterns.items():
                if any(kw in domain.lower() for kw in keywords):
                    findings.append({
                        'domain': domain,
                        'type': category,
                        'confidence': 'high'
                    })
                    break

        return findings

    def _prioritize_vulnerabilities(self, content: str) -> List[Dict[str, Any]]:
        """Prioritize vulnerability findings"""
        critical_keywords = ['rce', 'sql injection', 'xss', 'ssrf', 'idor']
        high_keywords = ['info disclosure', 'cors', 'csp', 'csrf']
        medium_keywords = ['misconfig', 'header', 'cookie']

        findings = []
        lines = content.strip().split('\n')

        for line in lines:
            line_lower = line.lower()
            severity = 'low'

            if any(kw in line_lower for kw in critical_keywords):
                severity = 'critical'
            elif any(kw in line_lower for kw in high_keywords):
                severity = 'high'
            elif any(kw in line_lower for kw in medium_keywords):
                severity = 'medium'

            findings.append({
                'finding': line.strip(),
                'severity': severity
            })

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        findings.sort(key=lambda x: severity_order.get(x['severity'], 4))

        return findings

    def _detect_wildcard_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect wildcard DNS patterns"""
        findings = []

        # Look for patterns like *.example.com
        if '*' in content or 'wildcard' in content.lower():
            findings.append({
                'pattern': 'wildcard_detected',
                'note': 'Wildcard DNS pattern found'
            })

        # Check for many subdomains resolving to same IP
        lines = content.strip().split('\n')
        ip_counts = {}

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[-1]
                ip_counts[ip] = ip_counts.get(ip, 0) + 1

        for ip, count in ip_counts.items():
            if count > 10:
                findings.append({
                    'pattern': 'multiple_to_same_ip',
                    'ip': ip,
                    'count': count,
                    'note': f'{count} subdomains resolve to same IP'
                })

        return findings
