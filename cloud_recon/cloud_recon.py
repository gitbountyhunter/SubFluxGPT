"""
Cloud Recon - SNI-IP Range Reconnaissance Module
Based on Jason Haddix's workflow with AI enhancements.
"""

import os
import re
import requests
import logging
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudRecon:
    """
    Main Cloud Recon class for SNI-IP range reconnaissance.
    Downloads, processes, and analyzes cloud provider SNI data.
    """

    # Cloud provider base URLs
    BASE_URL = "https://kaeferjaeger.gay/?dir=sni-ip-ranges"
    PROVIDERS = {
        'amazon': 'amazon',
        'digitalocean': 'digitalocean',
        'google': 'google',
        'microsoft': 'microsoft',
        'oracle': 'oracle'
    }

    def __init__(self, output_dir: str = './cloud_recon_data'):
        """
        Initialize Cloud Recon.

        Args:
            output_dir: Directory to store downloaded and processed data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.raw_dir = self.output_dir / 'raw'
        self.raw_dir.mkdir(exist_ok=True)

        self.processed_dir = self.output_dir / 'processed'
        self.processed_dir.mkdir(exist_ok=True)

        self.wildcards_dir = self.output_dir / 'wildcards'
        self.wildcards_dir.mkdir(exist_ok=True)

        self.apex_dir = self.output_dir / 'apex'
        self.apex_dir.mkdir(exist_ok=True)

        logger.info(f"Cloud Recon initialized with output directory: {self.output_dir}")

    def download_provider_data(self, provider: str) -> bool:
        """
        Download SNI-IP range data for a specific provider.

        Args:
            provider: Provider name (amazon, digitalocean, google, microsoft, oracle)

        Returns:
            True if successful
        """
        if provider not in self.PROVIDERS:
            logger.error(f"Unknown provider: {provider}")
            return False

        try:
            # Construct provider directory URL
            provider_url = f"{self.BASE_URL}/{provider}"
            logger.info(f"Fetching data from {provider_url}")

            # Get the directory listing
            response = requests.get(provider_url, timeout=30)
            response.raise_for_status()

            # Parse HTML to find .txt files
            import re
            file_pattern = re.compile(r'href="([^"]+\.txt)"')
            files = file_pattern.findall(response.text)

            if not files:
                logger.warning(f"No .txt files found for {provider}")
                return False

            logger.info(f"Found {len(files)} files for {provider}")

            # Download each file
            provider_dir = self.raw_dir / provider
            provider_dir.mkdir(exist_ok=True)

            for file in files:
                file_url = urljoin(provider_url, file)
                file_path = provider_dir / file

                logger.info(f"Downloading {file} from {provider}")
                file_response = requests.get(file_url, timeout=60)
                file_response.raise_for_status()

                with open(file_path, 'wb') as f:
                    f.write(file_response.content)

                logger.info(f"Downloaded {file} ({len(file_response.content)} bytes)")

            return True

        except Exception as e:
            logger.error(f"Failed to download data for {provider}: {e}")
            return False

    def download_all_providers(self) -> Dict[str, bool]:
        """
        Download data from all cloud providers in parallel.

        Returns:
            Dictionary mapping provider names to success status
        """
        logger.info("Starting download for all providers")

        results = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.download_provider_data, provider): provider
                for provider in self.PROVIDERS.keys()
            }

            for future in as_completed(futures):
                provider = futures[future]
                try:
                    results[provider] = future.result()
                except Exception as e:
                    logger.error(f"Error downloading {provider}: {e}")
                    results[provider] = False

        logger.info(f"Download complete: {sum(results.values())}/{len(results)} successful")
        return results

    def get_all_raw_files(self) -> List[Path]:
        """
        Get all downloaded raw .txt files.

        Returns:
            List of file paths
        """
        files = []
        for provider in self.PROVIDERS.keys():
            provider_dir = self.raw_dir / provider
            if provider_dir.exists():
                files.extend(provider_dir.glob('*.txt'))
        return files

    def process_provider_data(
        self,
        provider: str,
        apex_domain: Optional[str] = None,
        keep_wildcards: bool = False
    ) -> Dict[str, any]:
        """
        Process provider data using Jason Haddix's one-liner workflow.

        Args:
            provider: Provider name
            apex_domain: Filter by specific apex domain (e.g., "dell.com")
            keep_wildcards: Whether to keep wildcard domains

        Returns:
            Dictionary with processing results
        """
        provider_dir = self.raw_dir / provider
        if not provider_dir.exists():
            return {'success': False, 'error': f'No data for {provider}'}

        logger.info(f"Processing data for {provider}")

        # Concatenate all files for this provider
        all_content = []
        for file_path in provider_dir.glob('*.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_content.append(f.read())

        combined = '\n'.join(all_content)

        # Jason Haddix's one-liner logic (Python implementation)
        # Original: cat *.txt | grep ".dell.com" | grep -oP "(?<=\[).*(?=\])" | tr ' ' '\n' | grep -v "*" | sort -u

        results = {
            'provider': provider,
            'success': True,
            'apex_domain': apex_domain,
            'domains': set(),
            'wildcards': set(),
            'apex_domains': set(),
            'stats': {}
        }

        # Step 1: Filter by apex domain if specified
        if apex_domain:
            lines = [line for line in combined.split('\n') if apex_domain in line]
        else:
            lines = combined.split('\n')

        results['stats']['total_lines'] = len(lines)

        # Step 2: Extract domains from brackets (Jason's pattern)
        # Pattern: content between [ and ]
        bracket_pattern = re.compile(r'\[([^\]]+)\]')
        extracted = []

        for line in lines:
            matches = bracket_pattern.findall(line)
            if matches:
                extracted.extend(matches)
            else:
                # If no brackets, use the line as-is
                extracted.append(line.strip())

        results['stats']['extracted'] = len(extracted)

        # Step 3: Split by spaces and clean
        all_domains = []
        for item in extracted:
            # Remove brackets if present
            cleaned = re.sub(r'[\[\]]', '', item)
            # Split by spaces
            parts = cleaned.split()
            all_domains.extend(parts)

        results['stats']['split'] = len(all_domains)

        # Step 4: Separate wildcards and regular domains
        wildcards = set()
        regular_domains = set()

        for domain in all_domains:
            domain = domain.strip()
            if not domain:
                continue

            if '*' in domain:
                wildcards.add(domain)
            else:
                # Validate domain format
                if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
                    regular_domains.add(domain)

        results['wildcards'] = wildcards
        results['domains'] = regular_domains

        results['stats']['wildcards'] = len(wildcards)
        results['stats']['regular'] = len(regular_domains)

        # Step 5: Extract apex domains
        apex_domains = set()
        for domain in regular_domains:
            # Extract apex domain (e.g., api.example.com -> example.com)
            parts = domain.split('.')
            if len(parts) >= 2:
                apex = '.'.join(parts[-2:])
                apex_domains.add(apex)

        results['apex_domains'] = apex_domains
        results['stats']['apex'] = len(apex_domains)

        # Step 6: Deduplicate
        results['domains'] = sorted(list(regular_domains))
        results['wildcards'] = sorted(list(wildcards))
        results['apex_domains'] = sorted(list(apex_domains))

        results['stats']['final_domains'] = len(results['domains'])
        results['stats']['final_wildcards'] = len(results['wildcards'])
        results['stats']['final_apex'] = len(results['apex_domains'])

        # Save results
        if keep_wildcards:
            wildcard_file = self.wildcards_dir / f"{provider}_wildcards.txt"
            with open(wildcard_file, 'w') as f:
                f.write('\n'.join(results['wildcards']))
            logger.info(f"Saved wildcards to {wildcard_file}")

        domain_file = self.processed_dir / f"{provider}_domains.txt"
        with open(domain_file, 'w') as f:
            f.write('\n'.join(results['domains']))
        logger.info(f"Saved domains to {domain_file}")

        apex_file = self.apex_dir / f"{provider}_apex.txt"
        with open(apex_file, 'w') as f:
            f.write('\n'.join(results['apex_domains']))
        logger.info(f"Saved apex domains to {apex_file}")

        return results

    def process_all_providers(
        self,
        apex_domain: Optional[str] = None,
        keep_wildcards: bool = False
    ) -> Dict[str, Dict]:
        """
        Process all providers in parallel.

        Args:
            apex_domain: Filter by specific apex domain
            keep_wildcards: Whether to keep wildcard domains

        Returns:
            Dictionary mapping provider names to results
        """
        logger.info("Processing all providers")

        results = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(
                    self.process_provider_data,
                    provider,
                    apex_domain,
                    keep_wildcards
                ): provider
                for provider in self.PROVIDERS.keys()
            }

            for future in as_completed(futures):
                provider = futures[future]
                try:
                    results[provider] = future.result()
                except Exception as e:
                    logger.error(f"Error processing {provider}: {e}")
                    results[provider] = {'success': False, 'error': str(e)}

        # Create combined output
        all_domains = set()
        all_wildcards = set()
        all_apex = set()

        for provider, result in results.items():
            if result.get('success'):
                all_domains.update(result.get('domains', []))
                all_wildcards.update(result.get('wildcards', []))
                all_apex.update(result.get('apex_domains', []))

        # Save combined files
        combined_domain_file = self.processed_dir / 'all_providers_domains.txt'
        with open(combined_domain_file, 'w') as f:
            f.write('\n'.join(sorted(all_domains)))

        combined_wildcard_file = self.wildcards_dir / 'all_providers_wildcards.txt'
        with open(combined_wildcard_file, 'w') as f:
            f.write('\n'.join(sorted(all_wildcards)))

        combined_apex_file = self.apex_dir / 'all_providers_apex.txt'
        with open(combined_apex_file, 'w') as f:
            f.write('\n'.join(sorted(all_apex)))

        logger.info(f"Combined: {len(all_domains)} domains, {len(all_wildcards)} wildcards, {len(all_apex)} apex")

        results['combined'] = {
            'domains': sorted(all_domains),
            'wildcards': sorted(all_wildcards),
            'apex': sorted(all_apex),
            'stats': {
                'total_domains': len(all_domains),
                'total_wildcards': len(all_wildcards),
                'total_apex': len(all_apex)
            }
        }

        return results

    def export_for_bountycatch(
        self,
        project_name: str,
        use_apex: bool = False
    ) -> str:
        """
        Export processed domains in format for BountyCatch Remix.

        Args:
            project_name: Name for the project
            use_apex: Whether to export apex domains instead of full domains

        Returns:
            Path to exported file
        """
        if use_apex:
            source_file = self.apex_dir / 'all_providers_apex.txt'
        else:
            source_file = self.processed_dir / 'all_providers_domains.txt'

        if not source_file.exists():
            raise FileNotFoundError(f"No processed data found at {source_file}")

        # Create BountyCatch-compatible output
        bountycatch_dir = self.output_dir / 'bountycatch'
        bountycatch_dir.mkdir(exist_ok=True)

        output_file = bountycatch_dir / f"{project_name}.txt"

        with open(source_file, 'r') as src, open(output_file, 'w') as dst:
            content = src.read()
            dst.write(content)

        logger.info(f"Exported for BountyCatch: {output_file}")
        return str(output_file)

    def get_one_liner_commands(self, provider: str, apex_domain: str) -> List[str]:
        """
        Get the one-liner commands used for manual processing (Jason Haddix style).

        Args:
            provider: Provider name
            apex_domain: Apex domain to filter

        Returns:
            List of one-liner commands
        """
        commands = []

        # Command 1: Extract domains with wildcards
        cmd1 = f"cd {self.raw_dir / provider} && cat *.txt | grep -F \"{apex_domain}\" | grep -oP \"(?<=\\[).*(?=\\])\" | tr ' ' '\\n' | grep \"*\" | sort -u"
        commands.append({
            'description': 'Extract wildcard domains from SNI data',
            'command': cmd1
        })

        # Command 2: Extract domains without wildcards (clean)
        cmd2 = f"cd {self.raw_dir / provider} && cat *.txt | grep -F \"{apex_domain}\" | grep -oP \"(?<=\\[).*(?=\\])\" | tr ' ' '\\n' | grep -v \"*\" | sort -u > {self.processed_dir / provider}_clean.txt"
        commands.append({
            'description': 'Extract clean domains (no wildcards)',
            'command': cmd2
        })

        # Command 3: Apex domain extraction
        cmd3 = f"cat {self.processed_dir / provider}_clean.txt | awk -F. '{{print $(NF-1)\".\"$NF}}' | sort -u"
        commands.append({
            'description': 'Extract apex domains from clean list',
            'command': cmd3
        })

        # Command 4: Deduplicate all providers
        cmd4 = f"cat {self.processed_dir}/*.txt | sort -u > {self.processed_dir / 'all_combined.txt'}"
        commands.append({
            'description': 'Combine and deduplicate all providers',
            'command': cmd4
        })

        # Command 5: BountyCatch import
        cmd5 = f"python3 bountycatch.py add -p {provider}_{apex_domain.replace('.', '_')} -f {self.processed_dir / provider}_clean.txt"
        commands.append({
            'description': 'Import to BountyCatch Remix',
            'command': cmd5
        })

        return commands


class CloudReconManager:
    """
    Manager for Cloud Recon operations with AI analysis.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Cloud Recon Manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.cloud_recon = CloudRecon(
            output_dir=self.config.get('output_dir', './cloud_recon_data')
        )

    def run_full_workflow(
        self,
        apex_domain: Optional[str] = None,
        project_name: str = 'cloud_recon',
        ai_analysis: bool = True
    ) -> Dict[str, any]:
        """
        Run the complete Cloud Recon workflow.

        Args:
            apex_domain: Optional apex domain to filter
            project_name: Project name for BountyCatch
            ai_analysis: Whether to run AI analysis

        Returns:
            Complete workflow results
        """
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'apex_domain': apex_domain,
            'project_name': project_name,
            'steps': {}
        }

        # Step 1: Download all provider data
        logger.info("Step 1: Downloading cloud provider data")
        download_results = self.cloud_recon.download_all_providers()
        results['steps']['download'] = download_results

        # Step 2: Process all providers
        logger.info("Step 2: Processing SNI-IP range data")
        process_results = self.cloud_recon.process_all_providers(
            apex_domain=apex_domain,
            keep_wildcards=True
        )
        results['steps']['processing'] = process_results

        # Step 3: Export for BountyCatch
        logger.info("Step 3: Exporting for BountyCatch Remix")
        try:
            export_path = self.cloud_recon.export_for_bountycatch(project_name)
            results['steps']['export'] = {'success': True, 'path': export_path}
        except Exception as e:
            results['steps']['export'] = {'success': False, 'error': str(e)}

        # Step 4: AI Analysis (if enabled)
        if ai_analysis:
            logger.info("Step 4: Running AI analysis")
            try:
                from .ai_analyzer import CloudAIAnalyzer
                ai_analyzer = CloudAIAnalyzer(self.config)
                ai_results = ai_analyzer.analyze_cloud_assets(process_results)
                results['steps']['ai_analysis'] = ai_results
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                results['steps']['ai_analysis'] = {'success': False, 'error': str(e)}

        # Step 5: Generate one-liner commands
        logger.info("Step 5: Generating one-liner commands")
        if apex_domain:
            commands = {}
            for provider in self.cloud_recon.PROVIDERS.keys():
                commands[provider] = self.cloud_recon.get_one_liner_commands(
                    provider,
                    apex_domain
                )
            results['steps']['one_liners'] = commands

        logger.info("Cloud Recon workflow complete")
        return results
