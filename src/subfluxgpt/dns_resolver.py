"""
DNS Resolver with Wildcard Detection for SubFluxGPT
"""

import asyncio
import dns.resolver
import dns.exception
from typing import List, Optional, Set, Tuple
import random
import string


class DNSResolver:
    """DNS resolver with wildcard detection and validation"""

    def __init__(
        self,
        resolver: Optional[dns.resolver.Resolver] = None,
        timeout: float = 2.0,
        max_retries: int = 3
    ):
        """
        Initialize DNS resolver
        
        Args:
            resolver: Custom dns.resolver.Resolver instance
            timeout: Query timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.resolver = resolver or dns.resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout
        self.max_retries = max_retries
        self.wildcard_ips: Set[str] = set()
        self.wildcard_detected = False

    def detect_wildcard(self, domain: str) -> bool:
        """
        Detect if domain has wildcard DNS
        
        Args:
            domain: Target domain
            
        Returns:
            True if wildcard detected
        """
        # Generate random subdomains to test
        random_subs = [
            ''.join(random.choices(string.ascii_lowercase, k=16)) + domain
            for _ in range(3)
        ]
        
        ips = set()
        for sub in random_subs:
            try:
                answers = self.resolver.resolve(sub, "A")
                for answer in answers:
                    ips.add(answer.to_text())
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                continue
            except Exception:
                continue
        
        # If all random subdomains resolve to same IPs, it's a wildcard
        if len(ips) > 0:
            self.wildcard_ips = ips
            self.wildcard_detected = True
            return True
        
        return False

    async def resolve_subdomain(
        self,
        subdomain: str,
        record_types: List[str] = None
    ) -> dict:
        """
        Resolve a subdomain
        
        Args:
            subdomain: Subdomain to resolve
            record_types: List of record types to query (default: A, CNAME)
            
        Returns:
            Dictionary with resolution results
        """
        if record_types is None:
            record_types = ["A", "CNAME"]
        
        result = {
            "subdomain": subdomain,
            "resolved": False,
            "ips": [],
            "cnames": [],
            "error": None
        }
        
        for record_type in record_types:
            for attempt in range(self.max_retries):
                try:
                    answers = self.resolver.resolve(subdomain, record_type)
                    
                    if record_type == "A":
                        for answer in answers:
                            ip = answer.to_text()
                            # Check against wildcard IPs
                            if self.wildcard_detected and ip in self.wildcard_ips:
                                result["wildcard"] = True
                            result["ips"].append(ip)
                            result["resolved"] = True
                    
                    elif record_type == "CNAME":
                        for answer in answers:
                            result["cnames"].append(answer.to_text())
                            result["resolved"] = True
                    
                    break
                    
                except dns.resolver.NXDOMAIN:
                    result["error"] = "NXDOMAIN"
                    break
                except dns.resolver.NoAnswer:
                    # No records of this type, try next type
                    break
                except dns.resolver.Timeout:
                    if attempt == self.max_retries - 1:
                        result["error"] = "Timeout"
                    continue
                except Exception as e:
                    result["error"] = str(e)
                    break
        
        return result

    async def resolve_subdomains(
        self,
        subdomains: List[str],
        wildcard_check: bool = True,
        concurrent: int = 50
    ) -> List[dict]:
        """
        Resolve multiple subdomains concurrently
        
        Args:
            subdomains: List of subdomains to resolve
            wildcard_check: Whether to check for wildcards first
            concurrent: Number of concurrent resolutions
            
        Returns:
            List of resolution results
        """
        if not subdomains:
            return []
        
        # Extract domain for wildcard check
        domain = self._extract_domain(subdomains[0])
        
        if wildcard_check and domain:
            print("[*] Checking for wildcard DNS...", file=__import__("sys").stderr)
            if self.detect_wildcard(domain):
                print(f"[!] Wildcard DNS detected for {domain}", file=__import__("sys").stderr)
                print(f"[!] Wildcard IPs: {', '.join(self.wildcard_ips)}", file=__import__("sys").stderr)
        
        # Resolve subdomains in batches
        results = []
        semaphore = asyncio.Semaphore(concurrent)
        
        async def resolve_with_semaphore(sub):
            async with semaphore:
                return await self.resolve_subdomain(sub)
        
        tasks = [resolve_with_semaphore(sub) for sub in subdomains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        clean_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                clean_results.append({
                    "subdomain": subdomains[i],
                    "resolved": False,
                    "error": str(result)
                })
            else:
                clean_results.append(result)
        
        return clean_results

    def _extract_domain(self, hostname: str) -> str:
        """
        Extract domain from hostname
        
        Args:
            hostname: Full hostname
            
        Returns:
            Domain (e.g., example.com from sub.example.com)
        """
        parts = hostname.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return hostname

    def filter_resolved(self, results: List[dict]) -> List[str]:
        """
        Filter only successfully resolved subdomains
        
        Args:
            results: List of resolution results
            
        Returns:
            List of resolved subdomain names
        """
        return [r["subdomain"] for r in results if r["resolved"] and not r.get("wildcard")]

    def filter_wildcards(self, results: List[dict]) -> List[str]:
        """
        Filter out wildcard resolutions
        
        Args:
            results: List of resolution results
            
        Returns:
            List of non-wildcard subdomain names
        """
        return [r["subdomain"] for r in results if r["resolved"] and not r.get("wildcard")]

    def get_unique_ips(self, results: List[dict]) -> Set[str]:
        """
        Get unique IP addresses from results
        
        Args:
            results: List of resolution results
            
        Returns:
            Set of unique IPs
        """
        ips = set()
        for result in results:
            ips.update(result.get("ips", []))
        return ips

    async def validate_subdomain(self, subdomain: str) -> bool:
        """
        Quick validation check for a subdomain
        
        Args:
            subdomain: Subdomain to validate
            
        Returns:
            True if subdomain resolves
        """
        result = await self.resolve_subdomain(subdomain)
        return result["resolved"] and not result.get("wildcard")
