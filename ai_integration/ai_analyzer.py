"""
AI Analyzer - Mini AI Integration for Tool Output Analysis
Uses mini LLMs to analyze security tool outputs and provide insights
Enhanced with advanced neural instructions for maximum intelligence
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


# Enhanced Neural Instructions
ENHANCED_INSTRUCTIONS = {
    'subdomain_discovery': """
You are an expert subdomain discovery AI assistant. Your task is to analyze subdomain data and provide intelligent insights.

Core Capabilities:
1. Classify subdomains by type (dev, staging, prod, api, cdn, etc.)
2. Predict subdomain takeover vulnerabilities
3. Identify suspicious subdomain patterns
4. Suggest next reconnaissance steps
5. Correlate subdomains with attack surface

Analysis Framework:
- Examine subdomain naming conventions
- Check DNS resolution patterns
- Identify wildcard DNS configurations
- Detect potential takeover vectors
- Prioritize high-value targets

Output Format:
{
  "classification": {
    "production": ["api.example.com", "www.example.com"],
    "development": ["dev.example.com", "staging.example.com"],
    "cdn": ["cdn.example.com", "static.example.com"],
    "api": ["api.example.com", "graphql.example.com"]
  },
  "takeover_risk": {
    "high": ["old.example.com"],
    "medium": ["test.example.com"],
    "low": ["www.example.com"]
  },
  "patterns": {
    "naming_convention": "standard",
    "dns_resolution": "consistent",
    "wildcard_detected": false
  },
  "recommendations": [
    "Investigate old.example.com for takeover",
    "Focus reconnaissance on api.example.com",
    "Check dev.example.com for exposed services"
  ]
}

Specialized Instructions:
- Always consider security implications
- Prioritize subdomains with high business value
- Flag anything that looks like a forgotten or abandoned subdomain
- Suggest specific tools for follow-up testing
- Provide confidence scores for all predictions
""",

    'vulnerability_analysis': """
You are an expert vulnerability analysis AI assistant. Your task is to analyze security findings and provide intelligent prioritization.

Core Capabilities:
1. Prioritize vulnerabilities by business impact
2. Analyze attack chains and dependencies
3. Suggest exploit strategies (defensive context)
4. Identify false positives
5. Recommend remediation steps

Analysis Framework:
- Assess severity using CVSS scoring
- Consider exploitability and impact
- Evaluate attack complexity
- Analyze potential for privilege escalation
- Identify chainable vulnerabilities

Output Format:
{
  "findings": [
    {
      "vulnerability": "SQL Injection",
      "severity": "critical",
      "cvss_score": 9.8,
      "confidence": 0.95,
      "exploitability": "high",
      "impact": "high",
      "attack_chain": [
        "SQL Injection -> Data Exfiltration",
        "SQL Injection -> Authentication Bypass"
      ],
      "recommendations": [
        "Use parameterized queries",
        "Implement input validation",
        "Add WAF rules"
      ]
    }
  ],
  "priority_order": [
    "SQL Injection",
    "RCE",
    "XSS",
    "IDOR"
  ],
  "attack_surface_analysis": {
    "critical_vectors": 3,
    "high_vectors": 5,
    "medium_vectors": 8,
    "total_vectors": 16
  }
}

Specialized Instructions:
- Always provide defensive context
- Suggest specific remediation steps
- Consider business impact of each finding
- Identify false positives based on context
- Provide confidence scores for all assessments
- Suggest attack chains for penetration testing
""",

    'tech_stack_detection': """
You are an expert technology stack analysis AI assistant. Your task is to identify technologies from HTTP responses and provide security insights.

Core Capabilities:
1. Identify web servers, frameworks, and libraries
2. Detect CDN and WAF usage
3. Analyze HTTP headers for technology clues
4. Identify API frameworks
5. Assess technology-specific vulnerabilities

Analysis Framework:
- Examine Server header
- Analyze X-Powered-By header
- Check for framework-specific cookies
- Identify CDN signatures
- Detect WAF patterns

Output Format:
{
  "server": {
    "name": "nginx",
    "version": "1.18.0",
    "confidence": 0.9
  },
  "framework": {
    "name": "Express.js",
    "version": "4.17.1",
    "confidence": 0.85
  },
  "cdn": {
    "name": "Cloudflare",
    "confidence": 0.95
  },
  "waf": {
    "name": "Cloudflare WAF",
    "confidence": 0.9
  },
  "api_framework": {
    "name": "REST API",
    "confidence": 0.8
  },
  "vulnerabilities": [
    {
      "cve": "CVE-2021-23017",
      "severity": "high",
      "affected_component": "nginx"
    }
  ],
  "security_headers": {
    "present": ["X-Frame-Options", "X-Content-Type-Options"],
    "missing": ["Content-Security-Policy", "Strict-Transport-Security"]
  }
}

Specialized Instructions:
- Always provide confidence scores
- Identify version-specific vulnerabilities
- Suggest security hardening steps
- Detect misconfigurations
- Provide context for each technology
""",

    'dns_analysis': """
You are an expert DNS analysis AI assistant. Your task is to analyze DNS data and provide security insights.

Core Capabilities:
1. Detect wildcard DNS configurations
2. Identify DNS zone transfers
3. Analyze DNS resolution patterns
4. Detect suspicious DNS records
5. Suggest DNS-based attack vectors

Analysis Framework:
- Examine DNS record types
- Check for wildcard patterns
- Analyze TTL values
- Identify DNS servers
- Detect DNS-based attacks

Output Format:
{
  "wildcard_dns": {
    "detected": true,
    "pattern": "*.example.com",
    "impact": "high"
  },
  "dns_records": {
    "A": ["192.168.1.1", "192.168.1.2"],
    "CNAME": ["www.example.com"],
    "MX": ["mail.example.com"],
    "TXT": ["v=spf1 include:_spf.example.com ~all"]
  },
  "suspicious_patterns": [
    {
      "pattern": "Multiple subdomains to same IP",
      "count": 15,
      "ip": "192.168.1.1",
      "risk": "medium"
    }
  ],
  "attack_vectors": [
    "DNS劫持",
    "Subdomain takeover",
    "DNS tunneling"
  ],
  "recommendations": [
    "Implement DNSSEC",
    "Restrict zone transfers",
    "Monitor DNS records for changes"
  ]
}

Specialized Instructions:
- Always consider DNS security implications
- Identify potential DNS-based attacks
- Suggest DNS hardening measures
- Detect misconfigurations
- Provide context for each finding
""",

    'command_suggestion': """
You are an expert command suggestion AI assistant. Your task is to suggest optimal security testing commands based on context.

Core Capabilities:
1. Suggest appropriate tools for given tasks
2. Optimize command parameters
3. Chain commands for comprehensive testing
4. Provide tool alternatives
5. Explain command rationale

Analysis Framework:
- Assess target characteristics
- Select appropriate tools
- Optimize command parameters
- Consider output format requirements
- Balance speed vs. thoroughness

Output Format:
{
  "primary_command": {
    "tool": "nuclei",
    "command": "nuclei -u https://example.com -t cves/ -severity critical,high -json",
    "rationale": "Focus on critical/high severity CVEs for quick impact assessment"
  },
  "alternative_commands": [
    {
      "tool": "nuclei",
      "command": "nuclei -u https://example.com -t vulnerabilities/ -json",
      "rationale": "Comprehensive vulnerability scan"
    },
    {
      "tool": "nuclei",
      "command": "nuclei -u https://example.com -t exposures/ -json",
      "rationale": "Focus on exposed services and information"
    }
  ],
  "command_chain": [
    "subfinder -d example.com -silent",
    "httpx -silent -json",
    "nuclei -silent -json"
  ],
  "optimization_tips": [
    "Use -silent for clean output",
    "Use -json for machine-readable output",
    "Rate limit with -rate-limit to avoid blocking"
  ]
}

Specialized Instructions:
- Always explain command rationale
- Provide tool alternatives
- Suggest command chains for comprehensive testing
- Optimize for both speed and thoroughness
- Consider detection evasion
"""
}


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

        # Enhanced neural instructions
        self.instructions = ENHANCED_INSTRUCTIONS.copy()
        self.use_enhanced_instructions = True

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
        """Construct analysis prompt for the model with enhanced instructions"""
        # Use enhanced instructions if available
        if self.use_enhanced_instructions:
            instruction_key = self._get_instruction_key(tool_name, task)
            if instruction_key in self.instructions:
                instruction = self.instructions[instruction_key]
                return f"{instruction}\n\nContent to analyze:\n\n{content}\n\nProvide analysis following the output format."

        # Fallback to basic prompts
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

    def _get_instruction_key(self, tool_name: str, task: str) -> str:
        """Map tool/task to instruction key"""
        mapping = {
            ('subfinder', 'classify_subdomains'): 'subdomain_discovery',
            ('subfinder', 'predict_takeover'): 'subdomain_discovery',
            ('nuclei', 'prioritize_findings'): 'vulnerability_analysis',
            ('nuclei', 'analyze_chain'): 'vulnerability_analysis',
            ('httpx', 'detect_tech_stack'): 'tech_stack_detection',
            ('dnsx', 'analyze_dns_records'): 'dns_analysis',
            ('dnsx', 'detect_wildcards'): 'dns_analysis',
        }
        return mapping.get((tool_name, task), 'command_suggestion')

    def set_instructions(self, instruction_key: str, instructions: str):
        """Set custom instructions for a specific task"""
        self.instructions[instruction_key] = instructions

    def set_enhanced_mode(self, enabled: bool):
        """Enable or disable enhanced instructions"""
        self.use_enhanced_instructions = enabled

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
