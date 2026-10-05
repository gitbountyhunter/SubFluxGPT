"""
BBRF Client for SubFluxGPT
Integration with bug bounty reconnaissance framework
"""

import os
import asyncio
import aiohttp
from typing import List, Optional, Set
import json


class BBRFClient:
    """Client for BBRF (Bug Bounty Reconnaissance Framework)"""

    def __init__(
        self,
        server: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize BBRF client
        
        Args:
            server: BBRF server URL (defaults to BBRF_SERVER env var)
            username: BBRF username (defaults to BBRF_USERNAME env var)
            password: BBRF password (defaults to BBRF_PASSWORD env var)
        """
        self.server = server or os.getenv("BBRF_SERVER", "http://localhost:8080")
        self.username = username or os.getenv("BBRF_USERNAME")
        self.password = password or os.getenv("BBRF_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError(
                "BBRF credentials not found. Set BBRF_USERNAME and BBRF_PASSWORD environment variables"
            )
        
        self.auth_token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def authenticate(self) -> bool:
        """
        Authenticate with BBRF server
        
        Returns:
            True if authentication successful
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        auth_data = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            async with self.session.post(
                f"{self.server}/api/login",
                json=auth_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.auth_token = result.get("token")
                    return True
                else:
                    raise Exception(f"Authentication failed: {response.status}")
        except aiohttp.ClientError as e:
            raise Exception(f"BBRF connection error: {str(e)}")

    async def add_domains(
        self,
        domains: List[str],
        program: Optional[str] = None,
        scope_check: bool = True
    ) -> int:
        """
        Add domains to BBRF
        
        Args:
            domains: List of domains to add
            program: Optional program name for scoping
            scope_check: Whether to check against out-of-scope
            
        Returns:
            Number of domains added
        """
        if not self.auth_token:
            await self.authenticate()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        added_count = 0
        
        for domain in domains:
            # Check scope if enabled
            if scope_check and program:
                if await self.is_out_of_scope(domain, program):
                    print(f"[!] Skipping out-of-scope domain: {domain}", file=__import__("sys").stderr)
                    continue
            
            try:
                async with self.session.post(
                    f"{self.server}/api/domains",
                    headers=headers,
                    json={"domain": domain, "program": program}
                ) as response:
                    if response.status in [200, 201]:
                        added_count += 1
                    elif response.status == 409:
                        # Domain already exists
                        pass
                    else:
                        print(f"[!] Failed to add {domain}: {response.status}", file=__import__("sys").stderr)
            except Exception as e:
                print(f"[!] Error adding {domain}: {str(e)}", file=__import__("sys").stderr)
        
        return added_count

    async def get_program_scope(self, program: str) -> dict:
        """
        Get program scope (in-scope and out-of-scope)
        
        Args:
            program: Program name
            
        Returns:
            Dictionary with 'in_scope' and 'out_of_scope' lists
        """
        if not self.auth_token:
            await self.authenticate()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        try:
            async with self.session.get(
                f"{self.server}/api/programs/{program}/scope",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"in_scope": [], "out_of_scope": []}
        except Exception as e:
            print(f"[!] Error getting scope: {str(e)}", file=__import__("sys").stderr)
            return {"in_scope": [], "out_of_scope": []}

    async def is_out_of_scope(self, domain: str, program: str) -> bool:
        """
        Check if domain is out of scope for program
        
        Args:
            domain: Domain to check
            program: Program name
            
        Returns:
            True if out of scope
        """
        scope = await self.get_program_scope(program)
        
        for pattern in scope.get("out_of_scope", []):
            if domain.endswith(pattern) or pattern in domain:
                return True
        
        return False

    async def get_domains(self, program: Optional[str] = None) -> List[str]:
        """
        Get domains from BBRF
        
        Args:
            program: Optional program filter
            
        Returns:
            List of domains
        """
        if not self.auth_token:
            await self.authenticate()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        params = {}
        if program:
            params["program"] = program
        
        try:
            async with self.session.get(
                f"{self.server}/api/domains",
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("domains", [])
                else:
                    return []
        except Exception as e:
            print(f"[!] Error getting domains: {str(e)}", file=__import__("sys").stderr)
            return []

    async def create_program(self, program: str, description: str = "") -> bool:
        """
        Create a new program in BBRF
        
        Args:
            program: Program name
            description: Optional description
            
        Returns:
            True if successful
        """
        if not self.auth_token:
            await self.authenticate()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.post(
                f"{self.server}/api/programs",
                headers=headers,
                json={"name": program, "description": description}
            ) as response:
                return response.status in [200, 201]
        except Exception as e:
            print(f"[!] Error creating program: {str(e)}", file=__import__("sys").stderr)
            return False

    async def add_ip(self, ip: str, domain: str, program: Optional[str] = None) -> bool:
        """
        Add IP address to BBRF
        
        Args:
            ip: IP address
            domain: Associated domain
            program: Optional program
            
        Returns:
            True if successful
        """
        if not self.auth_token:
            await self.authenticate()
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.post(
                f"{self.server}/api/ips",
                headers=headers,
                json={"ip": ip, "domain": domain, "program": program}
            ) as response:
                return response.status in [200, 201]
        except Exception as e:
            print(f"[!] Error adding IP: {str(e)}", file=__import__("sys").stderr)
            return False

    @staticmethod
    def format_for_stdin(domains: List[str]) -> str:
        """
        Format domains for stdin piping
        
        Args:
            domains: List of domains
            
        Returns:
            Newline-separated string
        """
        return "\n".join(domains)
