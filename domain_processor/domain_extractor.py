"""
Domain extraction from bug bounty reports.
Extracts and validates domains and subdomains from report text.
"""

import re
import logging
import asyncio
from typing import List, Set, Optional, Dict, Any
from datetime import datetime
import dns.resolver
import tldextract
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractedDomain:
    """Data class for extracted domain information."""
    domain: str
    apex_domain: str
    tld: str
    context: str
    confidence: float  # 0.0 to 1.0


class DomainExtractor:
    """Extract domains from text using regex and validation."""
    
    # Domain regex pattern
    DOMAIN_PATTERN = re.compile(
        r'(?:https?://)?(?:www\.)?'
        r'(?:[a-zA-Z0-9-]+\.)+'  # Subdomains
        r'[a-zA-Z]{2,}'  # TLD
        r'(?:/[^\s]*)?',  # Optional path
        re.IGNORECASE
    )
    
    # Subdomain pattern
    SUBDOMAIN_PATTERN = re.compile(
        r'(?:[a-zA-Z0-9-]+\.){2,}'  # At least 2 dots (subdomain.domain.tld)
        r'[a-zA-Z]{2,}',
        re.IGNORECASE
    )
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize domain extractor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.validate_domains = config.get('validate_domains', True)
        self.validation_method = config.get('validation_method', 'async')
        self.dns_timeout = config.get('dns_timeout', 5)
        self.check_a_record = config.get('check_a_record', True)
        self.check_aaaa_record = config.get('check_aaaa_record', True)
        
        # Normalization options
        self.convert_to_lowercase = config.get('convert_to_lowercase', True)
        self.strip_www = config.get('strip_www', False)
        self.punycode_decode = config.get('punycode_decode', True)
        
        logger.info("Initialized DomainExtractor")
    
    def extract_domains(self, text: str) -> List[ExtractedDomain]:
        """
        Extract domains from text.
        
        Args:
            text: Text to extract domains from
            
        Returns:
            List of ExtractedDomain objects
        """
        if not text:
            return []
        
        domains = set()
        
        # Find all domain matches
        matches = self.DOMAIN_PATTERN.finditer(text)
        
        for match in matches:
            domain_str = match.group(0)
            
            # Clean up the domain
            domain_str = self._clean_domain(domain_str)
            
            if domain_str:
                domains.add(domain_str)
        
        # Convert to ExtractedDomain objects
        extracted = []
        for domain in domains:
            try:
                extracted_domain = self._parse_domain(domain, text)
                if extracted_domain:
                    extracted.append(extracted_domain)
            except Exception as e:
                logger.warning(f"Failed to parse domain {domain}: {e}")
        
        logger.info(f"Extracted {len(extracted)} unique domains from text")
        return extracted
    
    def _clean_domain(self, domain: str) -> Optional[str]:
        """
        Clean and normalize a domain string.
        
        Args:
            domain: Raw domain string
            
        Returns:
            Cleaned domain or None if invalid
        """
        try:
            # Remove protocol
            domain = re.sub(r'^https?://', '', domain)
            
            # Remove path
            domain = domain.split('/')[0]
            
            # Remove port
            domain = domain.split(':')[0]
            
            # Strip www if configured
            if self.strip_www:
                domain = re.sub(r'^www\.', '', domain)
            
            # Convert to lowercase
            if self.convert_to_lowercase:
                domain = domain.lower()
            
            # Basic validation
            if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
                return None
            
            return domain
            
        except Exception as e:
            logger.warning(f"Failed to clean domain {domain}: {e}")
            return None
    
    def _parse_domain(self, domain: str, context: str) -> Optional[ExtractedDomain]:
        """
        Parse domain into components.
        
        Args:
            domain: Domain string
            context: Original text context
            
        Returns:
            ExtractedDomain object or None if parsing fails
        """
        try:
            # Use tldextract to parse domain
            extracted = tldextract.extract(domain)
            
            if not extracted.suffix:
                return None
            
            apex_domain = f"{extracted.domain}.{extracted.suffix}"
            tld = extracted.suffix
            
            # Calculate confidence based on context
            confidence = self._calculate_confidence(domain, context)
            
            return ExtractedDomain(
                domain=domain,
                apex_domain=apex_domain,
                tld=tld,
                context=context[max(0, context.find(domain)-50):context.find(domain)+50],
                confidence=confidence
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse domain {domain}: {e}")
            return None
    
    def _calculate_confidence(self, domain: str, context: str) -> float:
        """
        Calculate confidence score for domain extraction.
        
        Args:
            domain: Extracted domain
            context: Original text context
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence if domain appears in typical contexts
        context_lower = context.lower()
        
        # Technical terms increase confidence
        if any(term in context_lower for term in ['vulnerability', 'endpoint', 'target', 'host']):
            confidence += 0.2
        
        # Protocol mentions increase confidence
        if 'http' in context_lower or 'dns' in context_lower:
            confidence += 0.1
        
        # Common subdomain patterns increase confidence
        if any(sub in domain for sub in ['api', 'www', 'dev', 'staging', 'test']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def validate_domain(self, domain: str) -> Dict[str, Any]:
        """
        Validate a domain using DNS lookups.
        
        Args:
            domain: Domain to validate
            
        Returns:
            Dictionary with validation results
        """
        if not self.validate_domains:
            return {'valid': True, 'method': 'none'}
        
        if self.validation_method == 'none':
            return {'valid': True, 'method': 'none'}
        
        try:
            results = {
                'domain': domain,
                'valid': False,
                'method': self.validation_method,
                'has_a_record': False,
                'has_aaaa_record': False,
                'error': None
            }
            
            # Check A record
            if self.check_a_record:
                try:
                    answers = dns.resolver.resolve(domain, 'A', lifetime=self.dns_timeout)
                    results['has_a_record'] = len(answers) > 0
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
                    pass
                except Exception as e:
                    results['error'] = str(e)
            
            # Check AAAA record
            if self.check_aaaa_record:
                try:
                    answers = dns.resolver.resolve(domain, 'AAAA', lifetime=self.dns_timeout)
                    results['has_aaaa_record'] = len(answers) > 0
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
                    pass
                except Exception as e:
                    if not results['error']:
                        results['error'] = str(e)
            
            # Domain is valid if it has any DNS records
            results['valid'] = results['has_a_record'] or results['has_aaaa_record']
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to validate domain {domain}: {e}")
            return {
                'domain': domain,
                'valid': False,
                'method': self.validation_method,
                'error': str(e)
            }
    
    async def validate_domains_batch(self, domains: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Validate multiple domains in parallel.
        
        Args:
            domains: List of domains to validate
            
        Returns:
            Dictionary mapping domain to validation results
        """
        if self.validation_method == 'none':
            return {domain: {'valid': True, 'method': 'none'} for domain in domains}
        
        tasks = [self.validate_domain(domain) for domain in domains]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = {}
        for domain, result in zip(domains, results_list):
            if isinstance(result, Exception):
                results[domain] = {
                    'domain': domain,
                    'valid': False,
                    'error': str(result)
                }
            else:
                results[domain] = result
        
        return results
    
    def extract_subdomains(self, text: str, apex_domain: str) -> List[str]:
        """
        Extract subdomains for a specific apex domain.
        
        Args:
            text: Text to search
            apex_domain: Apex domain to find subdomains for
            
        Returns:
            List of subdomain strings
        """
        if not text or not apex_domain:
            return []
        
        subdomains = set()
        
        # Find all matches
        matches = self.SUBDOMAIN_PATTERN.finditer(text)
        
        for match in matches:
            subdomain_str = match.group(0)
            
            # Clean up
            subdomain_str = self._clean_domain(subdomain_str)
            
            if subdomain_str and apex_domain in subdomain_str:
                subdomains.add(subdomain_str)
        
        return list(subdomains)
