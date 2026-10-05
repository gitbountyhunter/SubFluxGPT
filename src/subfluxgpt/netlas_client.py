"""
Netlas API Client for SubFluxGPT
Provides advanced attack surface reconnaissance
"""

import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class NetlasResult:
    """Normalized Netlas result"""
    domain: str
    ip: Optional[str] = None
    ports: List[int] = None
    services: List[str] = None
    title: Optional[str] = None
    technologies: List[str] = None
    certificates: List[str] = None

    def __post_init__(self):
        if self.ports is None:
            self.ports = []
        if self.services is None:
            self.services = []
        if self.technologies is None:
            self.technologies = []
        if self.certificates is None:
            self.certificates = []


class NetlasClient:
    """Client for Netlas.io API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Netlas client
        
        Args:
            api_key: Netlas API key (defaults to NETLAS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("NETLAS_API_KEY")
        if not self.api_key:
            raise ValueError("Netlas API key not found. Set NETLAS_API_KEY environment variable")
        
        self.base_url = "https://app.netlas.io/api"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search_domain(self, domain: str) -> List[NetlasResult]:
        """
        Search for domain-related data
        
        Args:
            domain: Target domain
            
        Returns:
            List of NetlasResult objects
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        query = f"domain:{domain}"
        results = await self._execute_query(query)
        return self._normalize_results(results)

    async def search_ip(self, ip: str) -> List[NetlasResult]:
        """
        Search for IP-related data
        
        Args:
            ip: Target IP address
            
        Returns:
            List of NetlasResult objects
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        query = f"ip:{ip}"
        results = await self._execute_query(query)
        return self._normalize_results(results)

    async def search_certificate(self, domain: str) -> List[str]:
        """
        Search for certificate data
        
        Args:
            domain: Target domain
            
        Returns:
            List of certificate subjects
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        query = f"certificate.subject:{domain}"
        results = await self._execute_query(query)
        
        certificates = []
        for result in results.get("data", []):
            cert_data = result.get("data", {})
            if "certificate" in cert_data:
                cert = cert_data["certificate"]
                if "subject" in cert:
                    certificates.append(cert["subject"])
        
        return certificates

    async def advanced_dork(self, dork: str) -> List[NetlasResult]:
        """
        Execute advanced dork query
        
        Args:
            dork: Netlas dork query
            
        Returns:
            List of NetlasResult objects
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        results = await self._execute_query(dork)
        return self._normalize_results(results)

    async def _execute_query(self, query: str, size: int = 100) -> Dict[str, Any]:
        """Execute Netlas query"""
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        params = {
            "q": query,
            "size": size
        }
        
        try:
            async with self.session.get(
                f"{self.base_url}/domains/",
                headers=headers,
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            raise Exception(f"Netlas API error: {str(e)}")

    def _normalize_results(self, raw_results: Dict[str, Any]) -> List[NetlasResult]:
        """
        Normalize Netlas results to save token space
        
        Args:
            raw_results: Raw Netlas API response
            
        Returns:
            List of normalized NetlasResult objects
        """
        normalized = []
        
        for item in raw_results.get("data", []):
            data = item.get("data", {})
            
            result = NetlasResult(
                domain=data.get("domain", ""),
                ip=data.get("ip"),
                ports=self._extract_ports(data),
                services=self._extract_services(data),
                title=data.get("http", {}).get("title"),
                technologies=self._extract_technologies(data),
                certificates=self._extract_certificates(data)
            )
            
            normalized.append(result)
        
        return normalized

    def _extract_ports(self, data: Dict[str, Any]) -> List[int]:
        """Extract open ports from data"""
        ports = []
        if "port" in data:
            ports.append(data["port"])
        if "ports" in data:
            ports.extend(data["ports"])
        return list(set(ports))

    def _extract_services(self, data: Dict[str, Any]) -> List[str]:
        """Extract service banners from data"""
        services = []
        if "service" in data:
            services.append(data["service"])
        if "services" in data:
            services.extend(data["services"])
        return list(set(services))

    def _extract_technologies(self, data: Dict[str, Any]) -> List[str]:
        """Extract technologies from HTTP data"""
        technologies = []
        http_data = data.get("http", {})
        
        if "server" in http_data:
            technologies.append(http_data["server"])
        
        if "technologies" in http_data:
            technologies.extend(http_data["technologies"])
        
        return list(set(technologies))

    def _extract_certificates(self, data: Dict[str, Any]) -> List[str]:
        """Extract certificate information"""
        certificates = []
        if "certificate" in data:
            cert = data["certificate"]
            if "subject" in cert:
                certificates.append(cert["subject"])
            if "issuer" in cert:
                certificates.append(f"Issuer: {cert['issuer']}")
        
        return certificates

    def results_to_summary(self, results: List[NetlasResult]) -> str:
        """
        Convert results to token-efficient summary for AI analysis
        
        Args:
            results: List of NetlasResult objects
            
        Returns:
            Summary string
        """
        if not results:
            return "No Netlas data found."
        
        summary_lines = ["Netlas Attack Surface Summary:"]
        
        for result in results[:20]:  # Limit to 20 for token efficiency
            line = f"- {result.domain}"
            if result.ip:
                line += f" ({result.ip})"
            if result.ports:
                line += f" Ports: {','.join(map(str, result.ports))}"
            if result.services:
                line += f" Services: {','.join(result.services[:3])}"
            if result.title:
                line += f" Title: {result.title[:50]}"
            summary_lines.append(line)
        
        return "\n".join(summary_lines)

    async def enrich_subdomains(
        self,
        subdomains: List[str]
    ) -> Dict[str, NetlasResult]:
        """
        Enrich subdomains with Netlas data
        
        Args:
            subdomains: List of subdomains to enrich
            
        Returns:
            Dictionary mapping subdomain to NetlasResult
        """
        enriched = {}
        
        for subdomain in subdomains:
            try:
                results = await self.search_domain(subdomain)
                if results:
                    enriched[subdomain] = results[0]
            except Exception as e:
                print(f"[!] Error enriching {subdomain}: {str(e)}", file=__import__("sys").stderr)
                continue
        
        return enriched
