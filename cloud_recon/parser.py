"""
SNI-IP Range Parser Module
Advanced parsing and extraction logic for cloud provider data.
"""

import re
import logging
from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class DomainInfo:
    """Information about a discovered domain."""
    domain: str
    provider: str
    is_wildcard: bool
    apex_domain: str
    confidence: float
    metadata: Dict


class SNIParser:
    """
    Advanced SNI-IP range parser with enhanced extraction capabilities.
    """

    # Patterns for different SNI data formats
    PATTERNS = {
        'bracketed': re.compile(r'\[([^\]]+)\]'),
        'quoted': re.compile(r'"([^"]+)"'),
        'comma_separated': re.compile(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'),
        'ip_range': re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
        'sni_pattern': re.compile(r'SNI:\s*([a-zA-Z0-9.-]+)'),
    }

    def __init__(self):
        """Initialize SNI Parser."""
        self.domain_cache = {}
        self.wildcard_cache = {}

    def parse_line(self, line: str, provider: str) -> List[DomainInfo]:
        """
        Parse a single line and extract domain information.

        Args:
            line: Line to parse
            provider: Cloud provider name

        Returns:
            List of DomainInfo objects
        """
        domains = []

        # Try different extraction patterns
        for pattern_name, pattern in self.PATTERNS.items():
            matches = pattern.findall(line)
            for match in matches:
                domain_info = self._create_domain_info(match, provider, pattern_name)
                if domain_info:
                    domains.append(domain_info)

        return domains

    def _create_domain_info(
        self,
        match: str,
        provider: str,
        pattern_source: str
    ) -> Optional[DomainInfo]:
        """
        Create DomainInfo from a match.

        Args:
            match: Matched string
            provider: Provider name
            pattern_source: Pattern that matched

        Returns:
            DomainInfo or None if invalid
        """
        # Clean the match
        cleaned = re.sub(r'[\[\]"\'<>]', '', match).strip()

        # Skip if too short or invalid
        if len(cleaned) < 4:
            return None

        # Check if it's a valid domain
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', cleaned):
            return None

        # Determine if wildcard
        is_wildcard = '*' in cleaned

        # Extract apex domain
        parts = cleaned.split('.')
        if len(parts) >= 2:
            apex = '.'.join(parts[-2:])
        else:
            apex = cleaned

        # Calculate confidence based on pattern source
        confidence_scores = {
            'bracketed': 0.95,
            'sni_pattern': 0.90,
            'quoted': 0.85,
            'comma_separated': 0.70,
            'ip_range': 0.30
        }
        confidence = confidence_scores.get(pattern_source, 0.50)

        return DomainInfo(
            domain=cleaned,
            provider=provider,
            is_wildcard=is_wildcard,
            apex_domain=apex,
            confidence=confidence,
            metadata={
                'pattern_source': pattern_source,
                'original_match': match
            }
        )

    def parse_file(self, file_path: str, provider: str) -> List[DomainInfo]:
        """
        Parse an entire file.

        Args:
            file_path: Path to file
            provider: Provider name

        Returns:
            List of DomainInfo objects
        """
        domains = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line_domains = self.parse_line(line, provider)
                    for domain_info in line_domains:
                        domain_info.metadata['line_number'] = line_num
                        domains.append(domain_info)

        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")

        return domains

    def deduplicate(self, domains: List[DomainInfo]) -> List[DomainInfo]:
        """
        Deduplicate domains while keeping highest confidence.

        Args:
            domains: List of DomainInfo objects

        Returns:
            Deduplicated list
        """
        domain_map = {}

        for domain_info in domains:
            key = domain_info.domain.lower()
            if key not in domain_map or domain_info.confidence > domain_map[key].confidence:
                domain_map[key] = domain_info

        return list(domain_map.values())

    def filter_wildcards(self, domains: List[DomainInfo]) -> Tuple[List[DomainInfo], List[DomainInfo]]:
        """
        Separate wildcards from regular domains.

        Args:
            domains: List of DomainInfo objects

        Returns:
            Tuple of (regular_domains, wildcard_domains)
        """
        regular = [d for d in domains if not d.is_wildcard]
        wildcards = [d for d in domains if d.is_wildcard]
        return regular, wildcards

    def group_by_apex(self, domains: List[DomainInfo]) -> Dict[str, List[DomainInfo]]:
        """
        Group domains by apex domain.

        Args:
            domains: List of DomainInfo objects

        Returns:
            Dictionary mapping apex domains to lists of domains
        """
        grouped = defaultdict(list)
        for domain_info in domains:
            grouped[domain_info.apex_domain].append(domain_info)
        return dict(grouped)

    def group_by_provider(self, domains: List[DomainInfo]) -> Dict[str, List[DomainInfo]]:
        """
        Group domains by provider.

        Args:
            domains: List of DomainInfo objects

        Returns:
            Dictionary mapping providers to lists of domains
        """
        grouped = defaultdict(list)
        for domain_info in domains:
            grouped[domain_info.provider].append(domain_info)
        return dict(grouped)

    def extract_tiered_domains(
        self,
        domains: List[DomainInfo],
        max_depth: int = 3
    ) -> Dict[str, List[str]]:
        """
        Extract domains by tier (apex, 2nd-level, 3rd-level, etc.).

        Args:
            domains: List of DomainInfo objects
            max_depth: Maximum subdomain depth to extract

        Returns:
            Dictionary mapping tier names to domain lists
        """
        tiers = defaultdict(list)

        for domain_info in domains:
            parts = domain_info.domain.split('.')
            depth = len(parts) - 2  # Subtract for TLD and 2LD

            if depth == 0:
                tiers['apex'].append(domain_info.domain)
            elif depth == 1:
                tiers['tier1'].append(domain_info.domain)
            elif depth == 2:
                tiers['tier2'].append(domain_info.domain)
            elif depth <= max_depth:
                tiers[f'tier{depth}'].append(domain_info.domain)
            else:
                tiers['deep'].append(domain_info.domain)

        return dict(tiers)

    def find_interesting_patterns(self, domains: List[DomainInfo]) -> Dict[str, List[str]]:
        """
        Find interesting patterns in domains (AI precursor).

        Args:
            domains: List of DomainInfo objects

        Returns:
            Dictionary mapping pattern types to domain lists
        """
        patterns = {
            'dev': [],
            'test': [],
            'staging': [],
            'api': [],
            'admin': [],
            'internal': [],
            'sandbox': [],
            'cdn': [],
            'cloud': [],
            'auth': []
        }

        for domain_info in domains:
            domain_lower = domain_info.domain.lower()
            for pattern, domain_list in patterns.items():
                if pattern in domain_lower:
                    domain_list.append(domain_info.domain)

        return patterns

    def generate_statistics(self, domains: List[DomainInfo]) -> Dict:
        """
        Generate statistics about parsed domains.

        Args:
            domains: List of DomainInfo objects

        Returns:
            Statistics dictionary
        """
        if not domains:
            return {}

        providers = set(d.provider for d in domains)
        apex_domains = set(d.apex_domain for d in domains)
        wildcards = sum(1 for d in domains if d.is_wildcard)

        # Average confidence
        avg_confidence = sum(d.confidence for d in domains) / len(domains)

        # Tier distribution
        tier_counts = defaultdict(int)
        for domain_info in domains:
            parts = domain_info.domain.split('.')
            depth = len(parts) - 2
            tier_counts[f'tier{depth}' if depth > 0 else 'apex'] += 1

        return {
            'total_domains': len(domains),
            'unique_domains': len(set(d.domain for d in domains)),
            'providers': list(providers),
            'provider_count': len(providers),
            'apex_domains': list(apex_domains),
            'apex_count': len(apex_domains),
            'wildcard_count': wildcards,
            'regular_count': len(domains) - wildcards,
            'average_confidence': round(avg_confidence, 3),
            'tier_distribution': dict(tier_counts)
        }
