"""
Utility functions for SubFluxGPT
"""

import re
import tldextract
from typing import List, Set, Optional


def extract_domain(subdomain: str) -> str:
    """
    Extract root domain from subdomain
    
    Args:
        subdomain: Full subdomain (e.g., api.example.com)
        
    Returns:
        Root domain (e.g., example.com)
    """
    extracted = tldextract.extract(subdomain)
    return f"{extracted.domain}.{extracted.suffix}"


def normalize_subdomain(subdomain: str, domain: str) -> str:
    """
    Normalize subdomain by removing domain suffix
    
    Args:
        subdomain: Full subdomain
        domain: Root domain
        
    Returns:
        Normalized subdomain prefix
    """
    subdomain = subdomain.strip()
    if subdomain.endswith(domain):
        return subdomain[:-len(domain)].rstrip('.')
    return subdomain


def validate_subdomain(subdomain: str) -> bool:
    """
    Basic subdomain validation
    
    Args:
        subdomain: Subdomain to validate
        
    Returns:
        True if valid
    """
    if not subdomain or len(subdomain) > 250:
        return False
    
    if ' ' in subdomain:
        return False
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9\-._*]+$', subdomain):
        return False
    
    return True


def deduplicate_subdomains(subdomains: List[str]) -> List[str]:
    """
    Remove duplicates while preserving order
    
    Args:
        subdomains: List of subdomains
        
    Returns:
        Deduplicated list
    """
    seen = set()
    result = []
    for sub in subdomains:
        if sub not in seen:
            seen.add(sub)
            result.append(sub)
    return result


def filter_subdomains(subdomains: List[str], patterns: List[str]) -> List[str]:
    """
    Filter subdomains by patterns
    
    Args:
        subdomains: List of subdomains
        patterns: List of patterns to include (supports wildcards)
        
    Returns:
        Filtered list
    """
    if not patterns:
        return subdomains
    
    filtered = []
    for sub in subdomains:
        for pattern in patterns:
            if pattern.startswith('*'):
                # Wildcard prefix
                if sub.endswith(pattern[1:]):
                    filtered.append(sub)
                    break
            elif pattern.endswith('*'):
                # Wildcard suffix
                if sub.startswith(pattern[:-1]):
                    filtered.append(sub)
                    break
            elif pattern in sub:
                # Contains
                filtered.append(sub)
                break
    
    return filtered


def chunk_subdomains(subdomains: List[str], chunk_size: int = 50) -> List[List[str]]:
    """
    Split subdomains into chunks
    
    Args:
        subdomains: List of subdomains
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [subdomains[i:i + chunk_size] for i in range(0, len(subdomains), chunk_size)]


def merge_subdomain_lists(*lists: List[str]) -> List[str]:
    """
    Merge multiple subdomain lists and deduplicate
    
    Args:
        *lists: Variable number of subdomain lists
        
    Returns:
        Merged and deduplicated list
    """
    merged = []
    seen = set()
    
    for lst in lists:
        for sub in lst:
            if sub not in seen:
                seen.add(sub)
                merged.append(sub)
    
    return merged


def read_subdomains_from_file(filepath: str) -> List[str]:
    """
    Read subdomains from file
    
    Args:
        filepath: Path to file
        
    Returns:
        List of subdomains
    """
    subdomains = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    subdomains.append(line)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {filepath}")
    
    return subdomains


def write_subdomains_to_file(subdomains: List[str], filepath: str) -> int:
    """
    Write subdomains to file
    
    Args:
        subdomains: List of subdomains
        filepath: Path to output file
        
    Returns:
        Number of subdomains written
    """
    with open(filepath, 'w') as f:
        for sub in subdomains:
            f.write(f"{sub}\n")
    
    return len(subdomains)


def calculate_token_count(text: str) -> int:
    """
    Estimate token count (rough approximation)
    
    Args:
        text: Text to count
        
    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4


def format_output(subdomains: List[str], output_format: str = "text") -> str:
    """
    Format subdomains for output
    
    Args:
        subdomains: List of subdomains
        output_format: Format type (text, json, csv)
        
    Returns:
        Formatted string
    """
    if output_format == "json":
        import json
        return json.dumps({"subdomains": subdomains}, indent=2)
    elif output_format == "csv":
        return "\n".join(subdomains)
    else:  # text
        return "\n".join(subdomains)


def parse_ai_response(response: str) -> List[str]:
    """
    Parse AI response to extract subdomains
    
    Args:
        response: AI response text
        
    Returns:
        List of extracted subdomains
    """
    subdomains = []
    
    for line in response.strip().split('\n'):
        line = line.strip()
        
        # Remove common prefixes
        line = line.lstrip('0123456789.-*•-–—')
        line = line.strip()
        
        # Validate
        if validate_subdomain(line):
            subdomains.append(line)
    
    return subdomains


def merge_with_known(generated: List[str], known: List[str]) -> List[str]:
    """
    Merge generated subdomains with known ones, removing duplicates
    
    Args:
        generated: AI-generated subdomains
        known: Known subdomains
        
    Returns:
        Merged list with new subdomains first
    """
    known_set = set(known)
    new_subs = [sub for sub in generated if sub not in known_set]
    
    return new_subs + known


def print_progress(current: int, total: int, prefix: str = "Progress") -> None:
    """
    Print progress bar to stderr
    
    Args:
        current: Current progress
        total: Total items
        prefix: Prefix text
    """
    import sys
    if total > 0:
        percent = int((current / total) * 100)
        print(f"\r{prefix}: {percent}% ({current}/{total})", file=sys.stderr, end="")
        if current == total:
            print(file=sys.stderr)
