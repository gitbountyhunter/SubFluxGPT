"""
External security tools integration for SubFluxGPT.
Wrappers for common bug bounty reconnaissance tools.
"""

import os
import logging
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class SecurityTool:
    """Base class for security tool wrappers."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize tool wrapper.

        Args:
            config: Tool configuration
        """
        self.enabled = config.get('enabled', False)
        self.binary_path = config.get('binary_path', config.get('name'))
        self.timeout = config.get('timeout', 300)
        self.options = config.get('options', {})

    def is_available(self) -> bool:
        """Check if tool is available."""
        if not self.enabled:
            return False

        try:
            result = subprocess.run(
                [self.binary_path, '-h'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"{self.binary_path} not available: {e}")
            return False

    def run(self, args: List[str], input_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the tool with arguments.

        Args:
            args: Command line arguments
            input_data: Optional input data via stdin

        Returns:
            Result with success status and output
        """
        if not self.is_available():
            return {'success': False, 'error': f'{self.binary_path} not available'}

        try:
            cmd = [self.binary_path] + args

            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout
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


class HTTPX(SecurityTool):
    """Wrapper for httpx - HTTP toolkit."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'httpx')

    def probe(self, targets: List[str], options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Probe targets for alive web servers.

        Args:
            targets: List of targets (domains/URLs)
            options: Additional options

        Returns:
            Result with alive hosts
        """
        opts = options or self.options

        args = [
            '-silent',
            '-json',
            '-status-code',
            '-title',
            '-tech-detect',
            '-content-length'
        ]

        if opts.get('timeout'):
            args.extend(['-timeout', str(opts['timeout'])])

        if opts.get('threads'):
            args.extend(['-threads', str(opts['threads'])])

        input_data = '\n'.join(targets)
        result = self.run(args, input_data=input_data)

        if result['success']:
            # Parse JSON output
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result

    def crawl(self, url: str, depth: int = 2) -> Dict[str, Any]:
        """
        Crawl a URL for endpoints.

        Args:
            url: URL to crawl
            depth: Crawl depth

        Returns:
            Result with discovered URLs
        """
        args = [
            '-silent',
            '-json',
            '-scrape',
            '-depth', str(depth),
            url
        ]

        result = self.run(args)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result


class Katana(SecurityTool):
    """Wrapper for katana - web crawler."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'katana')

    def crawl(self, url: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Crawl a URL for endpoints.

        Args:
            url: URL to crawl
            options: Additional options

        Returns:
            Result with discovered URLs
        """
        opts = options or self.options

        args = [
            '-u', url,
            '-silent',
            '-json',
            '-depth', str(opts.get('depth', 2)),
            '-js-crawl',
            '-field-scope', 'rdn'
        ]

        if opts.get('rate_limit'):
            args.extend(['-rate-limit', str(opts['rate_limit'])])

        result = self.run(args)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result


class Anew(SecurityTool):
    """Wrapper for anew - deduplication tool."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'anew')

    def deduplicate(self, items: List[str], file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Deduplicate items and add to file.

        Args:
            items: List of items to deduplicate
            file_path: File to store deduplicated items

        Returns:
            Result with new items
        """
        if file_path:
            args = [file_path]
        else:
            args = []

        input_data = '\n'.join(items)
        result = self.run(args, input_data=input_data)

        if result['success']:
            result['data'] = result['stdout'].strip().split('\n')

        return result


class GAU(SecurityTool):
    """Wrapper for gau - GetAllUrls."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'gau')

    def get_urls(self, domain: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get URLs from wayback machine for a domain.

        Args:
            domain: Domain to query
            options: Additional options

        Returns:
            Result with discovered URLs
        """
        opts = options or self.options

        args = [
            domain,
            '--subs',
            '--threads', str(opts.get('threads', 5))
        ]

        if opts.get('blacklist'):
            args.extend(['--blacklist', opts['blacklist']])

        result = self.run(args)

        if result['success']:
            result['data'] = result['stdout'].strip().split('\n')

        return result


class Nuclei(SecurityTool):
    """Wrapper for nuclei - vulnerability scanner."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'nuclei')

    def scan(self, targets: List[str], options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Scan targets for vulnerabilities.

        Args:
            targets: List of targets
            options: Additional options

        Returns:
            Result with vulnerabilities found
        """
        opts = options or self.options

        args = [
            '-silent',
            '-json',
            '-severity', opts.get('severity', 'medium,high,critical')
        ]

        if opts.get('templates'):
            args.extend(['-templates', opts['templates']])

        if opts.get('rate_limit'):
            args.extend(['-rate-limit', str(opts['rate_limit'])])

        input_data = '\n'.join(targets)
        result = self.run(args, input_data=input_data)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result

    def scan_url(self, url: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Scan a single URL for vulnerabilities.

        Args:
            url: URL to scan
            options: Additional options

        Returns:
            Result with vulnerabilities found
        """
        opts = options or self.options

        args = [
            '-u', url,
            '-silent',
            '-json',
            '-severity', opts.get('severity', 'medium,high,critical')
        ]

        if opts.get('templates'):
            args.extend(['-templates', opts['templates']])

        result = self.run(args)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result


class Naabu(SecurityTool):
    """Wrapper for naabu - port scanner."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'naabu')

    def scan(self, targets: List[str], options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Scan targets for open ports.

        Args:
            targets: List of targets
            options: Additional options

        Returns:
            Result with open ports
        """
        opts = options or self.options

        args = [
            '-silent',
            '-json',
            '-top-ports', str(opts.get('top_ports', 1000))
        ]

        if opts.get('ports'):
            args.extend(['-ports', opts['ports']])

        if opts.get('rate_limit'):
            args.extend(['-rate-limit', str(opts['rate_limit'])])

        input_data = '\n'.join(targets)
        result = self.run(args, input_data=input_data)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result


class DNSX(SecurityTool):
    """Wrapper for dnsx - DNS toolkit."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'dnsx')

    def resolve(self, domains: List[str], options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Resolve domains to IP addresses.

        Args:
            domains: List of domains
            options: Additional options

        Returns:
            Result with resolved domains
        """
        opts = options or self.options

        args = [
            '-silent',
            '-json',
            '-a',
            '-aaaa'
        ]

        if opts.get('resolver'):
            args.extend(['-r', opts['resolver']])

        input_data = '\n'.join(domains)
        result = self.run(args, input_data=input_data)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result


class MassDNS(SecurityTool):
    """Wrapper for massdns - high-performance DNS resolver."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'massdns')
        self.resolvers_file = config.get('resolvers_file', '/etc/resolvers.txt')

    def resolve(self, domains: List[str], options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Resolve domains using massdns.

        Args:
            domains: List of domains
            options: Additional options

        Returns:
            Result with resolved domains
        """
        opts = options or self.options

        args = [
            '-r', self.resolvers_file,
            '-t', 'A',
            '-o', 'S',
            '-s', str(opts.get('threads', 1000))
        ]

        input_data = '\n'.join([f"{domain} A" for domain in domains])
        result = self.run(args, input_data=input_data)

        if result['success']:
            # Parse massdns output
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    parts = line.split()
                    if len(parts) >= 3:
                        output.append({
                            'domain': parts[0],
                            'type': parts[1],
                            'ip': parts[2]
                        })
            result['data'] = output

        return result


class Amass(SecurityTool):
    """Wrapper for amass - attack surface discovery tool."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'amass')

    def enum(self, domain: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enumerate subdomains for a domain.

        Args:
            domain: Domain to enumerate
            options: Additional options

        Returns:
            Result with discovered subdomains
        """
        opts = options or self.options

        args = [
            'enum',
            '-passive',
            '-d', domain,
            '-json'
        ]

        if opts.get('timeout'):
            args.extend(['-timeout', str(opts['timeout'])])

        if opts.get('include_unresolvable'):
            args.append('-include-unresolvable')

        result = self.run(args)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result

    def intel(self, domain: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Gather intelligence on a domain.

        Args:
            domain: Domain to analyze
            options: Additional options

        Returns:
            Result with intelligence data
        """
        opts = options or self.options

        args = [
            'intel',
            '-d', domain,
            '-json'
        ]

        result = self.run(args)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result


class Hakrawler(SecurityTool):
    """Wrapper for hakrawler - web crawler."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'hakrawler')

    def crawl(self, url: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Crawl a URL for endpoints.

        Args:
            url: URL to crawl
            options: Additional options

        Returns:
            Result with discovered URLs
        """
        opts = options or self.options

        args = [
            '-url', url,
            '-depth', str(opts.get('depth', 3)),
            '-plain'
        ]

        if opts.get('scope'):
            args.extend(['-scope', opts['scope']])

        if opts.get('subs'):
            args.append('-subs')

        result = self.run(args)

        if result['success']:
            result['data'] = result['stdout'].strip().split('\n')

        return result

    def crawl_from_stdin(self, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Crawl URLs from stdin.

        Args:
            options: Additional options

        Returns:
            Result with discovered URLs
        """
        opts = options or self.options

        args = [
            '-depth', str(opts.get('depth', 3)),
            '-plain'
        ]

        if opts.get('scope'):
            args.extend(['-scope', opts['scope']])

        if opts.get('subs'):
            args.append('-subs')

        result = self.run(args)

        if result['success']:
            result['data'] = result['stdout'].strip().split('\n')

        return result


class Waybackurls(SecurityTool):
    """Wrapper for waybackurls - URLs from wayback machine."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'waybackurls')

    def get_urls(self, domain: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get URLs from wayback machine for a domain.

        Args:
            domain: Domain to query
            options: Additional options

        Returns:
            Result with discovered URLs
        """
        opts = options or self.options

        args = [domain]

        if opts.get('no_subs'):
            args.append('-no-subs')

        result = self.run(args)

        if result['success']:
            result['data'] = result['stdout'].strip().split('\n')

        return result


class Subfinder(SecurityTool):
    """Wrapper for subfinder - subdomain discovery tool."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'subfinder')

    def enum(self, domain: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Enumerate subdomains for a domain.

        Args:
            domain: Domain to enumerate
            options: Additional options

        Returns:
            Result with discovered subdomains
        """
        opts = options or self.options

        args = [
            'subfinder',
            '-d', domain,
            '-silent',
            '-json'
        ]

        if opts.get('all'):
            args.append('-all')

        if opts.get('threads'):
            args.extend(['-threads', str(opts['threads'])])

        result = self.run(args)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result


class Assetfinder(SecurityTool):
    """Wrapper for assetfinder - find domains and subdomains."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'assetfinder')

    def find(self, domain: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Find domains and subdomains related to a target.

        Args:
            domain: Domain to search
            options: Additional options

        Returns:
            Result with discovered domains
        """
        opts = options or self.options

        args = [
            '--subs-only',
            domain
        ]

        if opts.get('ignore'):
            args.extend(['--ignore', opts['ignore']])

        result = self.run(args)

        if result['success']:
            result['data'] = result['stdout'].strip().split('\n')

        return result


class Crtsh(SecurityTool):
    """Wrapper for crt.sh - certificate transparency log search."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # crt.sh is a web service, not a binary
        self.enabled = config.get('enabled', False)

    def query(self, domain: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Query crt.sh for subdomains.

        Args:
            domain: Domain to query
            options: Additional options

        Returns:
            Result with discovered subdomains
        """
        if not self.enabled:
            return {'success': False, 'error': 'crt.sh not enabled'}

        try:
            import requests

            opts = options or self.options
            url = f"https://crt.sh/?q=%.{domain}&output=json"

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Extract unique subdomains
            subdomains = set()
            for entry in data:
                name_value = entry.get('name_value', '')
                for name in name_value.split('\n'):
                    if name and not name.startswith('*'):
                        subdomains.add(name)

            result = {
                'success': True,
                'data': list(subdomains),
                'count': len(subdomains)
            }

            return result

        except Exception as e:
            return {'success': False, 'error': str(e)}


class FFUF(SecurityTool):
    """Wrapper for ffuf - web fuzzer."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'ffuf')

    def fuzz(self, url: str, wordlist: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fuzz a URL with a wordlist.

        Args:
            url: URL to fuzz (use FUZZ for injection point)
            wordlist: Path to wordlist
            options: Additional options

        Returns:
            Result with discovered paths
        """
        opts = options or self.options

        args = [
            '-u', url,
            '-w', wordlist,
            '-json',
            '-s'  # Silent mode
        ]

        if opts.get('threads'):
            args.extend(['-t', str(opts['threads'])])

        if opts.get('extensions'):
            args.extend(['-e', opts['extensions']])

        if opts.get('match_status'):
            args.extend(['-mc', opts['match_status']])

        result = self.run(args)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result


class Feroxbuster(SecurityTool):
    """Wrapper for feroxbuster - directory discovery tool."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'feroxbuster')

    def scan(self, url: str, wordlist: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Scan a URL for directories and files.

        Args:
            url: URL to scan
            wordlist: Path to wordlist
            options: Additional options

        Returns:
            Result with discovered paths
        """
        opts = options or self.options

        args = [
            '-u', url,
            '-w', wordlist,
            '--json',
            '--silent'
        ]

        if opts.get('threads'):
            args.extend(['-t', str(opts['threads'])])

        if opts.get('extensions'):
            args.extend(['-x', opts['extensions']])

        if opts.get('depth'):
            args.extend(['-d', str(opts['depth'])])

        result = self.run(args)

        if result['success']:
            output = []
            for line in result['stdout'].strip().split('\n'):
                if line:
                    try:
                        output.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            result['data'] = output

        return result


class Arjun(SecurityTool):
    """Wrapper for arjun - parameter discovery tool."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'arjun')

    def discover(self, url: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Discover parameters in a URL.

        Args:
            url: URL to analyze
            options: Additional options

        Returns:
            Result with discovered parameters
        """
        opts = options or self.options

        args = [
            '-u', url,
            '-oT'  # Output in text format
        ]

        if opts.get('headers'):
            args.extend(['-d', opts['headers']])

        result = self.run(args)

        if result['success']:
            result['data'] = result['stdout'].strip()

        return result


class Subjs(SecurityTool):
    """Wrapper for subjs - find subdomains in JavaScript files."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.binary_path = config.get('binary_path', 'subjs')

    def extract(self, urls: List[str], options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extract subdomains from JavaScript files.

        Args:
            urls: List of URLs to JavaScript files
            options: Additional options

        Returns:
            Result with discovered subdomains
        """
        opts = options or self.options

        input_data = '\n'.join(urls)
        result = self.run([], input_data=input_data)

        if result['success']:
            result['data'] = result['stdout'].strip().split('\n')

        return result


class SecurityToolManager:
    """Manager for all security tools."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize tool manager.

        Args:
            config: Full configuration dictionary
        """
        self.config = config
        self.tools_config = config.get('security_tools', {})

        # Initialize all tools
        self.httpx = HTTPX(self.tools_config.get('httpx', {}))
        self.katana = Katana(self.tools_config.get('katana', {}))
        self.anew = Anew(self.tools_config.get('anew', {}))
        self.gau = GAU(self.tools_config.get('gau', {}))
        self.nuclei = Nuclei(self.tools_config.get('nuclei', {}))
        self.naabu = Naabu(self.tools_config.get('naabu', {}))
        self.dnsx = DNSX(self.tools_config.get('dnsx', {}))
        self.massdns = MassDNS(self.tools_config.get('massdns', {}))
        self.amass = Amass(self.tools_config.get('amass', {}))
        self.hakrawler = Hakrawler(self.tools_config.get('hakrawler', {}))
        self.waybackurls = Waybackurls(self.tools_config.get('waybackurls', {}))
        self.subfinder = Subfinder(self.tools_config.get('subfinder', {}))
        self.assetfinder = Assetfinder(self.tools_config.get('assetfinder', {}))
        self.crtsh = Crtsh(self.tools_config.get('crtsh', {}))
        self.ffuf = FFUF(self.tools_config.get('ffuf', {}))
        self.feroxbuster = Feroxbuster(self.tools_config.get('feroxbuster', {}))
        self.arjun = Arjun(self.tools_config.get('arjun', {}))
        self.subjs = Subjs(self.tools_config.get('subjs', {}))

    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        available = []
        if self.httpx.is_available():
            available.append('httpx')
        if self.katana.is_available():
            available.append('katana')
        if self.anew.is_available():
            available.append('anew')
        if self.gau.is_available():
            available.append('gau')
        if self.nuclei.is_available():
            available.append('nuclei')
        if self.naabu.is_available():
            available.append('naabu')
        if self.dnsx.is_available():
            available.append('dnsx')
        if self.massdns.is_available():
            available.append('massdns')
        if self.amass.is_available():
            available.append('amass')
        if self.hakrawler.is_available():
            available.append('hakrawler')
        if self.waybackurls.is_available():
            available.append('waybackurls')
        if self.subfinder.is_available():
            available.append('subfinder')
        if self.assetfinder.is_available():
            available.append('assetfinder')
        if self.crtsh.enabled:
            available.append('crtsh')
        if self.ffuf.is_available():
            available.append('ffuf')
        if self.feroxbuster.is_available():
            available.append('feroxbuster')
        if self.arjun.is_available():
            available.append('arjun')
        if self.subjs.is_available():
            available.append('subjs')
        return available

    def run_reconnaissance(self, domain: str) -> Dict[str, Any]:
        """
        Run full reconnaissance on a domain.

        Args:
            domain: Domain to recon

        Returns:
            Results from all tools
        """
        results = {
            'domain': domain,
            'tools': {},
            'success': True
        }

        logger.info(f"Starting reconnaissance for {domain}")

        # Subdomain enumeration with multiple tools
        subdomains = set([domain])

        # Subfinder
        if self.subfinder.is_available():
            logger.info("Running subfinder")
            subfinder_result = self.subfinder.enum(domain)
            results['tools']['subfinder'] = subfinder_result
            for item in subfinder_result.get('data', []):
                if 'host' in item:
                    subdomains.add(item['host'])

        # Assetfinder
        if self.assetfinder.is_available():
            logger.info("Running assetfinder")
            assetfinder_result = self.assetfinder.find(domain)
            results['tools']['assetfinder'] = assetfinder_result
            for sub in assetfinder_result.get('data', []):
                subdomains.add(sub)

        # crt.sh
        if self.crtsh.enabled:
            logger.info("Running crt.sh")
            crtsh_result = self.crtsh.query(domain)
            results['tools']['crtsh'] = crtsh_result
            for sub in crtsh_result.get('data', []):
                subdomains.add(sub)

        # Amass
        if self.amass.is_available():
            logger.info("Running amass enumeration")
            amass_result = self.amass.enum(domain)
            results['tools']['amass'] = amass_result
            for item in amass_result.get('data', []):
                if 'name' in item:
                    subdomains.add(item['name'])

        # Convert to list
        subdomains = list(subdomains)
        logger.info(f"Found {len(subdomains)} unique subdomains")

        # Probe domains with httpx
        if self.httpx.is_available():
            logger.info("Running httpx probe")
            httpx_result = self.httpx.probe(subdomains)
            results['tools']['httpx'] = httpx_result

        # Get URLs from wayback machine (try both gau and waybackurls)
        if self.gau.is_available():
            logger.info("Running gau")
            gau_result = self.gau.get_urls(domain)
            results['tools']['gau'] = gau_result

        if self.waybackurls.is_available():
            logger.info("Running waybackurls")
            wayback_result = self.waybackurls.get_urls(domain)
            results['tools']['waybackurls'] = wayback_result

        # Crawl URLs
        if self.katana.is_available() and results['tools'].get('gau', {}).get('data'):
            logger.info("Running katana")
            urls = results['tools']['gau']['data'][:10]  # Limit to 10 for demo
            katana_results = []
            for url in urls:
                katana_result = self.katana.crawl(url)
                katana_results.append(katana_result)
            results['tools']['katana'] = katana_results

        # Also try hakrawler
        if self.hakrawler.is_available() and results['tools'].get('gau', {}).get('data'):
            logger.info("Running hakrawler")
            urls = results['tools']['gau']['data'][:10]
            hakrawler_results = []
            for url in urls:
                hakrawler_result = self.hakrawler.crawl(url)
                hakrawler_results.append(hakrawler_result)
            results['tools']['hakrawler'] = hakrawler_results

        # Vulnerability scan
        if self.nuclei.is_available():
            logger.info("Running nuclei")
            nuclei_result = self.nuclei.scan_url(f"http://{domain}")
            results['tools']['nuclei'] = nuclei_result

        # Directory fuzzing with ffuf
        if self.ffuf.is_available() and subdomains:
            logger.info("Running ffuf")
            # Fuzz first few subdomains
            wordlist = '/usr/share/wordlists/dirb/common.txt'  # Default, can be configured
            ffuf_results = []
            for sub in subdomains[:3]:  # Limit to 3 for demo
                url = f"http://{sub}/FUZZ"
                ffuf_result = self.ffuf.fuzz(url, wordlist)
                ffuf_results.append(ffuf_result)
            results['tools']['ffuf'] = ffuf_results

        # Directory fuzzing with feroxbuster
        if self.feroxbuster.is_available() and subdomains:
            logger.info("Running feroxbuster")
            wordlist = '/usr/share/wordlists/dirb/common.txt'
            feroxbuster_results = []
            for sub in subdomains[:3]:
                url = f"http://{sub}"
                feroxbuster_result = self.feroxbuster.scan(url, wordlist)
                feroxbuster_results.append(feroxbuster_result)
            results['tools']['feroxbuster'] = feroxbuster_results

        # Parameter discovery with arjun
        if self.arjun.is_available() and results['tools'].get('httpx', {}).get('data'):
            logger.info("Running arjun")
            arjun_results = []
            for item in results['tools']['httpx']['data'][:5]:  # Limit to 5 URLs
                if 'url' in item:
                    arjun_result = self.arjun.discover(item['url'])
                    arjun_results.append(arjun_result)
            results['tools']['arjun'] = arjun_results

        # JavaScript analysis with subjs
        if self.subjs.is_available() and results['tools'].get('gau', {}).get('data'):
            logger.info("Running subjs")
            # Extract JS URLs from gau results
            js_urls = [url for url in results['tools']['gau']['data'] if '.js' in url][:10]
            if js_urls:
                subjs_result = self.subjs.extract(js_urls)
                results['tools']['subjs'] = subjs_result

        logger.info(f"Reconnaissance complete for {domain}")
        return results
