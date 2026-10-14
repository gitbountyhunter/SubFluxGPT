"""
BBRF (Bug Bounty Reconnaissance Framework) integration for SubFluxGPT.
BBRF is a framework for managing and sharing reconnaissance data.
"""

import os
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests

logger = logging.getLogger(__name__)


class BBRFClient:
    """Client for interacting with BBRF."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize BBRF client.

        Args:
            config: BBRF configuration from config.yaml
        """
        self.enabled = config.get('enabled', False)
        self.api_endpoint = config.get('api_endpoint', 'http://localhost:5000')
        self.api_key = config.get('api_key', os.environ.get('BBRF_API_KEY', ''))
        self.workspace = config.get('workspace', 'subfluxgpt')
        self.username = config.get('username', 'subfluxgpt')

        if self.enabled and not self.api_key:
            logger.warning("BBRF enabled but no API key provided")

    def is_available(self) -> bool:
        """Check if BBRF is available."""
        if not self.enabled:
            return False

        try:
            response = requests.get(f"{self.api_endpoint}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"BBRF not available: {e}")
            return False

    def create_program(self, program: str, metadata: Optional[Dict] = None) -> bool:
        """
        Create a new program in BBRF.

        Args:
            program: Program name (e.g., "example.com")
            metadata: Optional metadata dictionary

        Returns:
            True if successful
        """
        if not self.is_available():
            return False

        try:
            payload = {
                'program': program,
                'workspace': self.workspace,
                'username': self.username,
                'metadata': metadata or {}
            }

            response = requests.post(
                f"{self.api_endpoint}/program",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Created BBRF program: {program}")
                return True
            else:
                logger.error(f"Failed to create program: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error creating program: {e}")
            return False

    def add_domain(self, program: str, domain: str, source: str = 'subfluxgpt') -> bool:
        """
        Add a domain to a program.

        Args:
            program: Program name
            domain: Domain to add
            source: Source of the domain

        Returns:
            True if successful
        """
        if not self.is_available():
            return False

        try:
            payload = {
                'program': program,
                'domain': domain,
                'source': source,
                'workspace': self.workspace,
                'username': self.username
            }

            response = requests.post(
                f"{self.api_endpoint}/domain",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Added domain to BBRF: {domain}")
                return True
            else:
                logger.error(f"Failed to add domain: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error adding domain: {e}")
            return False

    def add_subdomain(self, program: str, subdomain: str, source: str = 'subfluxgpt') -> bool:
        """
        Add a subdomain to a program.

        Args:
            program: Program name
            subdomain: Subdomain to add
            source: Source of the subdomain

        Returns:
            True if successful
        """
        if not self.is_available():
            return False

        try:
            payload = {
                'program': program,
                'subdomain': subdomain,
                'source': source,
                'workspace': self.workspace,
                'username': self.username
            }

            response = requests.post(
                f"{self.api_endpoint}/subdomain",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Added subdomain to BBRF: {subdomain}")
                return True
            else:
                logger.error(f"Failed to add subdomain: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error adding subdomain: {e}")
            return False

    def add_url(self, program: str, url: str, status_code: Optional[int] = None, source: str = 'subfluxgpt') -> bool:
        """
        Add a URL to a program.

        Args:
            program: Program name
            url: URL to add
            status_code: HTTP status code (optional)
            source: Source of the URL

        Returns:
            True if successful
        """
        if not self.is_available():
            return False

        try:
            payload = {
                'program': program,
                'url': url,
                'status_code': status_code,
                'source': source,
                'workspace': self.workspace,
                'username': self.username
            }

            response = requests.post(
                f"{self.api_endpoint}/url",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Added URL to BBRF: {url}")
                return True
            else:
                logger.error(f"Failed to add URL: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error adding URL: {e}")
            return False

    def add_vulnerability(self, program: str, vulnerability: Dict[str, Any]) -> bool:
        """
        Add a vulnerability to a program.

        Args:
            program: Program name
            vulnerability: Vulnerability details

        Returns:
            True if successful
        """
        if not self.is_available():
            return False

        try:
            payload = {
                'program': program,
                'vulnerability': vulnerability,
                'workspace': self.workspace,
                'username': self.username
            }

            response = requests.post(
                f"{self.api_endpoint}/vulnerability",
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Added vulnerability to BBRF")
                return True
            else:
                logger.error(f"Failed to add vulnerability: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error adding vulnerability: {e}")
            return False

    def get_domains(self, program: str) -> List[str]:
        """
        Get all domains for a program.

        Args:
            program: Program name

        Returns:
            List of domains
        """
        if not self.is_available():
            return []

        try:
            response = requests.get(
                f"{self.api_endpoint}/domains/{program}",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get('domains', [])
            else:
                logger.error(f"Failed to get domains: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error getting domains: {e}")
            return []

    def get_subdomains(self, program: str) -> List[str]:
        """
        Get all subdomains for a program.

        Args:
            program: Program name

        Returns:
            List of subdomains
        """
        if not self.is_available():
            return []

        try:
            response = requests.get(
                f"{self.api_endpoint}/subdomains/{program}",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get('subdomains', [])
            else:
                logger.error(f"Failed to get subdomains: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error getting subdomains: {e}")
            return []

    def sync_from_bbrf(self, program: str) -> Dict[str, List[str]]:
        """
        Sync data from BBRF for a program.

        Args:
            program: Program name

        Returns:
            Dictionary with domains, subdomains, urls
        """
        return {
            'domains': self.get_domains(program),
            'subdomains': self.get_subdomains(program)
        }


class BBRFCLI:
    """Wrapper for BBRF CLI commands."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize BBRF CLI wrapper.

        Args:
            config: BBRF configuration
        """
        self.enabled = config.get('enabled', False)
        self.workspace = config.get('workspace', 'subfluxgpt')

    def run_command(self, command: List[str]) -> Dict[str, Any]:
        """
        Run a BBRF CLI command.

        Args:
            command: Command and arguments

        Returns:
            Result with success status and output
        """
        if not self.enabled:
            return {'success': False, 'error': 'BBRF not enabled'}

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300
            )

            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def new_scope(self, domain: str) -> Dict[str, Any]:
        """
        Create a new scope in BBRF.

        Args:
            domain: Domain for the scope

        Returns:
            Command result
        """
        return self.run_command(['bbrf', 'new', 'scope', domain])

    def scope_add(self, domain: str) -> Dict[str, Any]:
        """
        Add domain to scope.

        Args:
            domain: Domain to add

        Returns:
            Command result
        """
        return self.run_command(['bbrf', 'scope', 'add', domain])

    def domains(self) -> Dict[str, Any]:
        """
        List all domains in current scope.

        Returns:
            Command result
        """
        return self.run_command(['bbrf', 'domains'])

    def subdomains(self) -> Dict[str, Any]:
        """
        List all subdomains in current scope.

        Returns:
            Command result
        """
        return self.run_command(['bbrf', 'subdomains'])

    def urls(self) -> Dict[str, Any]:
        """
        List all URLs in current scope.

        Returns:
            Command result
        """
        return self.run_command(['bbrf', 'urls'])

    def inscope(self, domain: str) -> Dict[str, Any]:
        """
        Check if domain is in scope.

        Args:
            domain: Domain to check

        Returns:
            Command result
        """
        return self.run_command(['bbrf', 'inscope', domain])
