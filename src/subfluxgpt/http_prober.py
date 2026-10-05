"""
HTTP Prober using httpx for SubFluxGPT
"""

import asyncio
import httpx
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class HTTPResult:
    """HTTP probe result"""
    url: str
    status_code: Optional[int] = None
    title: Optional[str] = None
    content_length: Optional[int] = None
    server: Optional[str] = None
    technologies: List[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []


class HTTPProber:
    """HTTP prober using httpx"""

    def __init__(
        self,
        timeout: float = 10.0,
        max_redirects: int = 5,
        user_agent: str = "SubFluxGPT/1.0",
        verify_ssl: bool = True
    ):
        """
        Initialize HTTP prober
        
        Args:
            timeout: Request timeout in seconds
            max_redirects: Maximum redirect depth
            user_agent: User-Agent string
            verify_ssl: Whether to verify SSL certificates
        """
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.user_agent = user_agent
        self.verify_ssl = verify_ssl
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            max_redirects=self.max_redirects,
            verify=self.verify_ssl,
            headers={"User-Agent": self.user_agent}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def probe_url(self, url: str) -> HTTPResult:
        """
        Probe a single URL
        
        Args:
            url: URL to probe
            
        Returns:
            HTTPResult with probe data
        """
        if not self.client:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                max_redirects=self.max_redirects,
                verify=self.verify_ssl,
                headers={"User-Agent": self.user_agent}
            )
        
        result = HTTPResult(url=url)
        
        try:
            response = await self.client.get(url)
            result.status_code = response.status_code
            result.content_length = len(response.content)
            
            # Extract headers
            headers = response.headers
            result.server = headers.get("server", "")
            
            # Extract title from HTML
            try:
                content = response.text
                if "<title>" in content.lower():
                    start = content.lower().find("<title>") + 7
                    end = content.lower().find("</title>", start)
                    if end > start:
                        result.title = content[start:end].strip()[:100]
            except Exception:
                pass
            
            # Extract technologies from headers
            technologies = []
            if "x-powered-by" in headers:
                technologies.append(headers["x-powered-by"])
            if "server" in headers:
                technologies.append(headers["server"])
            result.technologies = technologies
            
        except httpx.TimeoutException:
            result.error = "Timeout"
        except httpx.ConnectError:
            result.error = "Connection Error"
        except httpx.HTTPStatusError as e:
            result.status_code = e.response.status_code
            result.error = f"HTTP Error: {e.response.status_code}"
        except Exception as e:
            result.error = str(e)
        
        return result

    async def probe_subdomains(
        self,
        subdomains: List[str],
        scheme: str = "https",
        concurrent: int = 50
    ) -> List[HTTPResult]:
        """
        Probe multiple subdomains
        
        Args:
            subdomains: List of subdomains to probe
            scheme: URL scheme (http or https)
            concurrent: Number of concurrent probes
            
        Returns:
            List of HTTPResult objects
        """
        if not subdomains:
            return []
        
        # Build URLs
        urls = [f"{scheme}://{sub}" for sub in subdomains]
        
        # Probe concurrently
        semaphore = asyncio.Semaphore(concurrent)
        
        async def probe_with_semaphore(url):
            async with semaphore:
                return await self.probe_url(url)
        
        tasks = [probe_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        clean_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                clean_results.append(HTTPResult(url=urls[i], error=str(result)))
            else:
                clean_results.append(result)
        
        return clean_results

    async def probe_both_schemes(
        self,
        subdomains: List[str],
        concurrent: int = 50
    ) -> Dict[str, Dict[str, HTTPResult]]:
        """
        Probe subdomains on both HTTP and HTTPS
        
        Args:
            subdomains: List of subdomains to probe
            concurrent: Number of concurrent probes
            
        Returns:
            Dictionary mapping subdomain to {http: result, https: result}
        """
        if not subdomains:
            return {}
        
        results = {}
        
        # Probe HTTPS first
        https_results = await self.probe_subdomains(subdomains, scheme="https", concurrent=concurrent)
        
        # Probe HTTP for those that failed on HTTPS
        http_subdomains = []
        for i, result in enumerate(https_results):
            subdomain = subdomains[i]
            results[subdomain] = {"https": result}
            
            # Try HTTP if HTTPS failed or redirected
            if result.error or (result.status_code and result.status_code >= 400):
                http_subdomains.append(subdomain)
        
        if http_subdomains:
            http_results = await self.probe_subdomains(http_subdomains, scheme="http", concurrent=concurrent)
            for i, result in enumerate(http_results):
                subdomain = http_subdomains[i]
                results[subdomain]["http"] = result
        
        return results

    def filter_alive(self, results: List[HTTPResult]) -> List[str]:
        """
        Filter only successfully probed URLs
        
        Args:
            results: List of HTTPResult objects
            
        Returns:
            List of URLs that responded successfully
        """
        return [r.url for r in results if r.status_code and r.status_code < 500]

    def filter_by_status(self, results: List[HTTPResult], status_codes: List[int]) -> List[str]:
        """
        Filter by specific status codes
        
        Args:
            results: List of HTTPResult objects
            status_codes: List of status codes to match
            
        Returns:
            List of URLs with matching status codes
        """
        return [r.url for r in results if r.status_code in status_codes]

    def get_unique_servers(self, results: List[HTTPResult]) -> Set[str]:
        """
        Get unique server headers
        
        Args:
            results: List of HTTPResult objects
            
        Returns:
            Set of unique server strings
        """
        servers = set()
        for result in results:
            if result.server:
                servers.add(result.server)
        return servers

    def results_to_summary(self, results: List[HTTPResult]) -> str:
        """
        Convert results to summary string
        
        Args:
            results: List of HTTPResult objects
            
        Returns:
            Summary string
        """
        if not results:
            return "No HTTP results."
        
        summary_lines = ["HTTP Probe Summary:"]
        
        for result in results[:30]:  # Limit to 30 for readability
            line = f"- {result.url}"
            if result.status_code:
                line += f" [{result.status_code}]"
            if result.title:
                line += f" - {result.title[:50]}"
            if result.server:
                line += f" ({result.server})"
            summary_lines.append(line)
        
        return "\n".join(summary_lines)
